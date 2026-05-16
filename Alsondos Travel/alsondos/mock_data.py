# mock_data.py — Sample data for all modules

USERS = [
    {"id": 1, "username": "admin", "password": "admin123", "role": "admin", "name": "Ahmad Al-Rashid", "email": "admin@alsondos.com"},
    {"id": 2, "username": "employee", "password": "emp123", "role": "employee", "name": "Sara Hassan", "email": "sara@alsondos.com"},
    {"id": 3, "username": "accountant", "password": "acc123", "role": "accountant", "name": "Khaled Nour", "email": "khaled@alsondos.com"},
    {"id": 4, "username": "omar", "password": "omar123", "role": "employee", "name": "Omar Ziad", "email": "omar@alsondos.com"},
]

COMPANIES = [
    {"id": 1, "name": "Gulf Air Travel Co.", "contact": "Mohammed Al-Khalid", "phone": "+962-6-555-0101", "email": "info@gulfair-travel.com", "balance": 4850.00},
    {"id": 2, "name": "Levant Tours LLC", "contact": "Rania Barakat", "phone": "+962-6-555-0202", "email": "rania@levanttours.com", "balance": 12300.00},
    {"id": 3, "name": "Jordan Star Agency", "contact": "Hassan Moussa", "phone": "+962-6-555-0303", "email": "h.moussa@jordanstar.jo", "balance": -2100.00},
    {"id": 4, "name": "Petra Travel Group", "contact": "Lina Suleiman", "phone": "+962-6-555-0404", "email": "lina@petratravel.com", "balance": 7650.00},
    {"id": 5, "name": "Amman Wings Corp.", "contact": "Faris Khaleel", "phone": "+962-6-555-0505", "email": "faris@ammanwings.com", "balance": 980.00},
]

SUPPLIERS = [
    {"id": 1, "name": "Royal Jordanian Airlines"},
    {"id": 2, "name": "Emirates Airlines"},
    {"id": 3, "name": "Turkish Airlines"},
    {"id": 4, "name": "Flydubai"},
    {"id": 5, "name": "Air Arabia"},
    {"id": 6, "name": "Qatar Airways"},
]

TRANSACTIONS = [
    {"id": 1001, "supplier": "Royal Jordanian", "company": "Gulf Air Travel Co.", "customer": "Ahmad Mansour", "from_city": "Amman", "to_city": "Dubai", "departure": "2024-12-20", "return_date": "2024-12-27", "buy_from": "Direct", "return_supplier": "Royal Jordanian", "buy_price": 180.00, "sell_price": 245.00, "status": "Delivered", "notes": "Business class upgrade", "employee": "Sara Hassan", "created_at": "2024-12-01"},
    {"id": 1002, "supplier": "Emirates Airlines", "company": "Levant Tours LLC", "customer": "Nour Al-Ahmad", "from_city": "Amman", "to_city": "London", "departure": "2025-01-05", "return_date": "2025-01-15", "buy_from": "GDS", "return_supplier": "Emirates Airlines", "buy_price": 520.00, "sell_price": 695.00, "status": "Pending", "notes": "Group booking - 4 pax", "employee": "Sara Hassan", "created_at": "2024-12-03"},
    {"id": 1003, "supplier": "Turkish Airlines", "company": "Jordan Star Agency", "customer": "Hiba Khalil", "from_city": "Amman", "to_city": "Istanbul", "departure": "2024-12-28", "return_date": "2025-01-03", "buy_from": "Consolidator", "return_supplier": "Turkish Airlines", "buy_price": 290.00, "sell_price": 375.00, "status": "Delivered", "notes": "", "employee": "Omar Ziad", "created_at": "2024-12-05"},
    {"id": 1004, "supplier": "Flydubai", "company": "Petra Travel Group", "customer": "Samir Jaber", "from_city": "Amman", "to_city": "Bangkok", "departure": "2025-01-10", "return_date": "2025-01-24", "buy_from": "Direct", "return_supplier": "Flydubai", "buy_price": 640.00, "sell_price": 820.00, "status": "Confirmed", "notes": "Honeymoon package", "employee": "Sara Hassan", "created_at": "2024-12-07"},
    {"id": 1005, "supplier": "Air Arabia", "company": "Amman Wings Corp.", "customer": "Dina Saleh", "from_city": "Amman", "to_city": "Cairo", "departure": "2024-12-18", "return_date": "2024-12-22", "buy_from": "GDS", "return_supplier": "Air Arabia", "buy_price": 95.00, "sell_price": 145.00, "status": "Delivered", "notes": "Urgent booking", "employee": "Omar Ziad", "created_at": "2024-12-08"},
    {"id": 1006, "supplier": "Qatar Airways", "company": "Gulf Air Travel Co.", "customer": "Tariq Hamdan", "from_city": "Amman", "to_city": "New York", "departure": "2025-02-14", "return_date": "2025-02-28", "buy_from": "Direct", "return_supplier": "Qatar Airways", "buy_price": 980.00, "sell_price": 1250.00, "status": "Pending", "notes": "First class", "employee": "Sara Hassan", "created_at": "2024-12-10"},
    {"id": 1007, "supplier": "Royal Jordanian", "company": "Levant Tours LLC", "customer": "Rana Farouk", "from_city": "Amman", "to_city": "Paris", "departure": "2025-01-20", "return_date": "2025-01-30", "buy_from": "GDS", "return_supplier": "Royal Jordanian", "buy_price": 610.00, "sell_price": 780.00, "status": "Confirmed", "notes": "Business travel", "employee": "Omar Ziad", "created_at": "2024-12-11"},
    {"id": 1008, "supplier": "Emirates Airlines", "company": "Petra Travel Group", "customer": "Ziad Abu-Omar", "from_city": "Amman", "to_city": "Singapore", "departure": "2025-03-05", "return_date": "2025-03-15", "buy_from": "Consolidator", "return_supplier": "Emirates Airlines", "buy_price": 750.00, "sell_price": 960.00, "status": "Pending", "notes": "", "employee": "Sara Hassan", "created_at": "2024-12-12"},
]

PAYMENTS = [
    {"id": 201, "company": "Gulf Air Travel Co.", "amount": 2000.00, "method": "Bank Transfer", "date": "2024-12-05", "notes": "Partial payment Dec", "received_by": "Khaled Nour"},
    {"id": 202, "company": "Levant Tours LLC", "amount": 5000.00, "method": "Cheque", "date": "2024-12-06", "notes": "Cheque #44521", "received_by": "Khaled Nour"},
    {"id": 203, "company": "Jordan Star Agency", "amount": 1500.00, "method": "Cash", "date": "2024-12-07", "notes": "Cash payment office", "received_by": "Ahmad Al-Rashid"},
    {"id": 204, "company": "Petra Travel Group", "amount": 3000.00, "method": "Bank Transfer", "date": "2024-12-08", "notes": "Wire transfer ARAB BANK", "received_by": "Khaled Nour"},
    {"id": 205, "company": "Gulf Air Travel Co.", "amount": 1250.00, "method": "Cash", "date": "2024-12-10", "notes": "", "received_by": "Sara Hassan"},
    {"id": 206, "company": "Amman Wings Corp.", "amount": 750.00, "method": "Bank Transfer", "date": "2024-12-11", "notes": "Advance payment Jan", "received_by": "Khaled Nour"},
    {"id": 207, "company": "Levant Tours LLC", "amount": 2800.00, "method": "Cheque", "date": "2024-12-12", "notes": "Cheque #44587", "received_by": "Khaled Nour"},
]

HOTELS = [
    {"id": 1, "name": "Grand Hyatt Amman", "city": "Amman", "stars": 5},
    {"id": 2, "name": "Kempinski Hotel Ishtar", "city": "Dead Sea", "stars": 5},
    {"id": 3, "name": "Marriott Dead Sea Resort", "city": "Dead Sea", "stars": 5},
    {"id": 4, "name": "Hilton Amman", "city": "Amman", "stars": 5},
    {"id": 5, "name": "Petra Marriott Hotel", "city": "Petra", "stars": 4},
]

AUDIT_LOG = [
    {"id": 1, "user": "Ahmad Al-Rashid", "action": "Created Transaction #1006", "item": "Transaction", "timestamp": "2024-12-10 09:14:22"},
    {"id": 2, "user": "Sara Hassan", "action": "Updated Transaction #1002 status → Pending", "item": "Transaction", "timestamp": "2024-12-10 10:30:05"},
    {"id": 3, "user": "Khaled Nour", "action": "Recorded Payment #206 — Amman Wings Corp.", "item": "Payment", "timestamp": "2024-12-11 11:05:44"},
    {"id": 4, "user": "Omar Ziad", "action": "Created Transaction #1007", "item": "Transaction", "timestamp": "2024-12-11 13:22:10"},
    {"id": 5, "user": "Ahmad Al-Rashid", "action": "Generated Statement — Levant Tours LLC", "item": "Statement", "timestamp": "2024-12-12 08:45:30"},
    {"id": 6, "user": "Sara Hassan", "action": "Created Hotel Voucher — Grand Hyatt Amman", "item": "Voucher", "timestamp": "2024-12-12 09:10:00"},
    {"id": 7, "user": "Khaled Nour", "action": "Recorded Payment #207 — Levant Tours LLC", "item": "Payment", "timestamp": "2024-12-12 14:00:15"},
    {"id": 8, "user": "Omar Ziad", "action": "Created Transaction #1008", "item": "Transaction", "timestamp": "2024-12-12 15:30:00"},
]

DASHBOARD_STATS = {
    "total_sales": 85450.00,
    "total_collected": 61250.00,
    "total_balance": 24200.00,
    "pending_deliveries": 4,
    "transactions_count": 8,
    "companies_count": 5,
    "monthly_growth": 12.5,
    "top_employees": [
        {"name": "Sara Hassan", "sales": 42300, "commission": 2115},
        {"name": "Omar Ziad", "sales": 28150, "commission": 1407},
        {"name": "Ahmad Al-Rashid", "sales": 15000, "commission": 750},
    ],
    "unpaid_companies": [
        {"name": "Jordan Star Agency", "balance": -2100.00},
        {"name": "Amman Wings Corp.", "balance": 980.00},
    ],
    "recent_activity": AUDIT_LOG[:5],
    "monthly_sales": [
        {"month": "Jul", "amount": 52000},
        {"month": "Aug", "amount": 61000},
        {"month": "Sep", "amount": 48000},
        {"month": "Oct", "amount": 70000},
        {"month": "Nov", "amount": 79000},
        {"month": "Dec", "amount": 85450},
    ]
}
