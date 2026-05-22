# fee-management-system
This is for a school to manage their collected fee

To run on your system:
**What to copy:**
- The entire project folder (`Fee Management System/`)  — this includes the database (db.sqlite3), all code, and the .env file

**What to install on the new laptop:**
1. **Python** (same version — 3.9.4 or close)
2. Run once:
   ```
   cd "Fee Management System"
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

That's it — no other changes needed. The database (all students, fees, users) travels with the db.sqlite3 file inside the folder.

**Easiest way to transfer:** Copy the folder via USB drive or shared network folder — but **exclude the venv folder** (it's large and must be recreated on the new machine anyway). Everything else must be copied.

