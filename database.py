import sqlite3
import os

DB_PATH = "chiplink.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        model       TEXT NOT NULL,
        brand       TEXT NOT NULL,
        category    TEXT NOT NULL,
        package     TEXT,
        description TEXT,
        specs       TEXT,
        stock       INTEGER DEFAULT 0,
        cost_price  REAL DEFAULT 0,
        sale_price  REAL DEFAULT 0,
        min_qty     INTEGER DEFAULT 1,
        is_domestic INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS inquiries (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        inquiry_no   TEXT UNIQUE,
        model        TEXT NOT NULL,
        brand        TEXT,
        quantity     INTEGER NOT NULL,
        target_price REAL,
        quoted_price REAL,
        company      TEXT,
        contact      TEXT,
        phone        TEXT,
        email        TEXT,
        delivery     TEXT,
        need_date    TEXT,
        notes        TEXT,
        status       TEXT DEFAULT 'pending',
        created_at   TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS orders (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no    TEXT UNIQUE,
        company     TEXT,
        contact     TEXT,
        phone       TEXT,
        total       REAL,
        tax         REAL,
        status      TEXT DEFAULT 'confirmed',
        notes       TEXT,
        created_at  TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id   INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        model      TEXT,
        quantity   INTEGER,
        unit_price REAL
    );

    CREATE TABLE IF NOT EXISTS alt_products (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        original_model TEXT NOT NULL,
        alt_model     TEXT NOT NULL,
        alt_brand     TEXT NOT NULL,
        compat_level  TEXT,
        description   TEXT,
        tags          TEXT,
        orig_price    REAL,
        alt_price     REAL
    );

    CREATE TABLE IF NOT EXISTS cart_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        product_id INTEGER REFERENCES products(id),
        model      TEXT,
        quantity   INTEGER DEFAULT 1,
        unit_price REAL
    );
    """)

    # Seed products if empty
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            ("STM32F103C8T6","ST","MCU","LQFP48","ARM Cortex-M3 · 72MHz · 64KB Flash","主频72MHz,Flash64KB,RAM20KB,LQFP48",12500,6.20,8.50,1000,0),
            ("NRF52840-QIAA-R","Nordic","无线","QFN73","BLE 5.0 · 64MHz · 1MB Flash","主频64MHz,BLE5.0,Zigbee,USB",2100,24.00,32.00,500,0),
            ("GD32F303RCT6","兆易创新","MCU","LQFP64","国产MCU · 120MHz · 256KB Flash","主频120MHz,Flash256KB,RAM48KB",8000,4.80,6.80,1000,1),
            ("W25Q128JVSIQ","Winbond","存储","SOP8","NOR Flash · 128Mb · SPI","128Mb,SPI接口,3.3V",500,3.10,4.20,2000,0),
            ("TPS62130ARGTR","TI","功率","QFN20","DC-DC降压 · 3A · 17V输入","3A,17Vin,可调输出,高效率",0,9.50,12.50,500,0),
            ("ESP32-S3-WROOM-1","乐鑫","无线","模组","WiFi+BT · Xtensa · 16MB Flash","WiFi6,BLE5.0,16MB,丰富外设",5500,13.00,18.00,500,1),
            ("GD25Q128CSIG","兆易创新","存储","SOP8","国产NOR Flash · 128Mb · SPI","128Mb,兼容W25Q128,国产替代",15000,2.50,3.80,2000,1),
            ("APM32F103C8T6","极海半导体","MCU","LQFP48","国产MCU · 低功耗 · STM32兼容","引脚兼容STM32F103,低功耗优化",6000,4.20,6.20,1000,1),
        ]
        c.executemany("""INSERT INTO products
            (model,brand,category,package,description,specs,stock,cost_price,sale_price,min_qty,is_domestic)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", products)

    # Seed alt products if empty
    c.execute("SELECT COUNT(*) FROM alt_products")
    if c.fetchone()[0] == 0:
        alts = [
            ("STM32F103C8T6","GD32F103C8T6","兆易创新","完全兼容","完全引脚兼容，主频108MHz，固件基本无需修改，量产验证广泛","引脚完全兼容,固件兼容,量产验证",8.50,5.80),
            ("STM32F103C8T6","APM32F103C8T6","极海半导体","完全兼容","引脚兼容，集成硬件除法器，功耗更低，工业级认证齐全","引脚完全兼容,低功耗优化,需评估验证",8.50,6.20),
            ("STM32F103C8T6","CKS32F103C8T6","中科芯","基本兼容","性价比极高，价格最低，适合大批量成本敏感项目","性价比最优,需测试验证",8.50,4.50),
            ("W25Q128JVSIQ","GD25Q128CSIG","兆易创新","完全兼容","完全引脚兼容，SPI接口一致，可直接替换","引脚完全兼容,固件兼容,量产验证",4.20,2.80),
            ("NRF52840-QIAA-R","DA14531MOD","Dialog","功能相近","超低功耗BLE，适合穿戴设备，价格更低","低功耗BLE,需重新开发",32.00,18.00),
        ]
        c.executemany("""INSERT INTO alt_products
            (original_model,alt_model,alt_brand,compat_level,description,tags,orig_price,alt_price)
            VALUES (?,?,?,?,?,?,?,?)""", alts)

    # Seed inquiries if empty
    c.execute("SELECT COUNT(*) FROM inquiries")
    if c.fetchone()[0] == 0:
        inqs = [
            ("INQ-0892","STM32F103C8T6","ST",5000,8.00,None,"深圳某科技","张工","138xxxx0001","zhang@company.com","深圳","2026-06-15","需原装正品","pending"),
            ("INQ-0891","NRF52840-QIAA-R","Nordic",1000,30.00,None,"广州电子厂","李采购","139xxxx0002","li@factory.com","广州","2026-06-20","","pending"),
            ("INQ-0890","GD32F303RCT6","兆易创新",20000,None,6.50,"苏州某智能","王工","137xxxx0003","wang@smart.com","苏州","2026-07-01","接受国产品牌","quoted"),
            ("INQ-0889","TPS62130ARGTR","TI",5000,11.00,11.50,"上海某仪器","陈经理","136xxxx0004","chen@inst.com","上海","2026-06-10","","confirmed"),
        ]
        c.executemany("""INSERT INTO inquiries
            (inquiry_no,model,brand,quantity,target_price,quoted_price,company,contact,phone,email,delivery,need_date,notes,status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", inqs)

    # Seed orders if empty
    c.execute("SELECT COUNT(*) FROM orders")
    if c.fetchone()[0] == 0:
        orders = [
            ("ORD-2025051","深圳某科技有限公司","张工","138xxxx0001",42500,5525,"processing"),
            ("ORD-2025050","广州电子制造厂","李采购","139xxxx0002",32000,4160,"shipped"),
            ("ORD-2025049","苏州某智能设备","王工","137xxxx0003",41000,5330,"confirmed"),
            ("ORD-2025048","上海某汽车电子","陈经理","136xxxx0004",25000,3250,"shipped"),
        ]
        c.executemany("""INSERT INTO orders (order_no,company,contact,phone,total,tax,status)
            VALUES (?,?,?,?,?,?,?)""", orders)

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")
