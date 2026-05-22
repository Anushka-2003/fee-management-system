/**
 * FEE MANAGEMENT SYSTEM – DATA LAYER
 * All data is stored in localStorage. No server required.
 */
const FeeDB = {

  // ==============================
  // STUDENT CRUD
  // ==============================
  getStudents() {
    return JSON.parse(localStorage.getItem('fms_students') || '[]');
  },
  saveStudents(students) {
    localStorage.setItem('fms_students', JSON.stringify(students));
  },
  addStudent(data) {
    const students = this.getStudents();
    const student = {
      ...data,
      id: 'S' + Date.now(),
      serialNo: this._nextSerial(),
      createdAt: new Date().toISOString()
    };
    students.push(student);
    this.saveStudents(students);
    return student;
  },
  updateStudent(id, data) {
    const students = this.getStudents();
    const idx = students.findIndex(s => s.id === id);
    if (idx === -1) return null;
    students[idx] = { ...students[idx], ...data, id, serialNo: students[idx].serialNo };
    this.saveStudents(students);
    return students[idx];
  },
  deleteStudent(id) {
    this.saveStudents(this.getStudents().filter(s => s.id !== id));
    this.saveFees(this.getFees().filter(f => f.studentId !== id));
  },
  getStudentById(id) {
    return this.getStudents().find(s => s.id === id) || null;
  },
  getStudentsByClass(cls) {
    const all = this.getStudents();
    if (!cls || cls === 'all') return all;
    return all.filter(s => s.class === cls);
  },
  searchStudents(query) {
    const q = (query || '').toLowerCase();
    if (!q) return this.getStudents();
    return this.getStudents().filter(s =>
      s.name.toLowerCase().includes(q) ||
      (s.fatherName || '').toLowerCase().includes(q) ||
      String(s.serialNo).includes(q) ||
      (s.rollNo || '').toString().includes(q) ||
      (s.phone || '').includes(q)
    );
  },
  _nextSerial() {
    const students = this.getStudents();
    if (!students.length) return 1;
    return Math.max(...students.map(s => s.serialNo || 0)) + 1;
  },

  // ==============================
  // FEE CRUD
  // ==============================
  getFees() {
    return JSON.parse(localStorage.getItem('fms_fees') || '[]');
  },
  saveFees(fees) {
    localStorage.setItem('fms_fees', JSON.stringify(fees));
  },
  addFee(data) {
    const fees = this.getFees();
    const fee = {
      ...data,
      id: 'F' + Date.now(),
      receiptNo: this._nextReceiptNo(),
      total: this.calcTotal(data),
      createdAt: new Date().toISOString()
    };
    fees.push(fee);
    this.saveFees(fees);
    return fee;
  },
  updateFee(id, data) {
    const fees = this.getFees();
    const idx = fees.findIndex(f => f.id === id);
    if (idx === -1) return null;
    fees[idx] = { ...fees[idx], ...data, id, receiptNo: fees[idx].receiptNo, total: this.calcTotal({ ...fees[idx], ...data }) };
    this.saveFees(fees);
    return fees[idx];
  },
  deleteFee(id) {
    this.saveFees(this.getFees().filter(f => f.id !== id));
  },
  getFeeById(id) {
    return this.getFees().find(f => f.id === id) || null;
  },
  getFeesByStudent(studentId) {
    return this.getFees().filter(f => f.studentId === studentId);
  },
  getFeesBySession(session) {
    if (!session || session === 'all') return this.getFees();
    return this.getFees().filter(f => f.session === session);
  },
  calcTotal(fee) {
    return (parseFloat(fee.tuitionFee) || 0)
         + (parseFloat(fee.registrationFee) || 0)
         + (parseFloat(fee.examFee) || 0)
         + (parseFloat(fee.miscFee) || 0);
  },
  _nextReceiptNo() {
    const fees = this.getFees();
    const year = new Date().getFullYear();
    const count = fees.length + 1;
    return `RCP-${year}-${String(count).padStart(4, '0')}`;
  },

  // ==============================
  // STATISTICS
  // ==============================
  getTodayCollection() {
    const today = new Date().toISOString().split('T')[0];
    return this.getFees()
      .filter(f => f.paymentDate === today)
      .reduce((s, f) => s + (f.total || 0), 0);
  },
  getMonthCollection() {
    const now = new Date();
    return this.getFees()
      .filter(f => {
        const d = new Date(f.paymentDate);
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      })
      .reduce((s, f) => s + (f.total || 0), 0);
  },
  getSessionCollection(session) {
    return this.getFeesBySession(session).reduce((s, f) => s + (f.total || 0), 0);
  },
  getRecentFees(limit = 10) {
    return [...this.getFees()]
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, limit);
  },
  getDefaulters(session, month) {
    const paidStudentIds = new Set(
      this.getFees()
        .filter(f => f.session === session && f.month === month)
        .map(f => f.studentId)
    );
    return this.getStudents().filter(s => !paidStudentIds.has(s.id));
  },

  // ==============================
  // AUTH
  // ==============================
  getUsers() {
    const defaults = [
      { username: 'admin',   password: 'admin123',   role: 'admin', name: 'Administrator' },
      { username: 'teacher', password: 'teacher123', role: 'user',  name: 'Teacher' }
    ];
    return JSON.parse(localStorage.getItem('fms_users') || JSON.stringify(defaults));
  },
  authenticate(username, password) {
    return this.getUsers().find(u => u.username === username && u.password === password) || null;
  },

  // ==============================
  // APP SESSION (academic session)
  // ==============================
  getCurrentSession() {
    return localStorage.getItem('fms_current_session') || '2026-2027';
  },
  setCurrentSession(s) {
    localStorage.setItem('fms_current_session', s);
  },

  // ==============================
  // SEED DEMO DATA
  // ==============================
  seedData() {
    if (localStorage.getItem('fms_seeded')) return;

    const classes   = ['Nursery', 'KG', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5'];
    const sections  = ['A', 'B'];
    const firstNames = ['Rahul', 'Priya', 'Amit', 'Sunita', 'Rajesh', 'Meena', 'Vikram', 'Kavita', 'Suresh', 'Anita', 'Deepak', 'Pooja', 'Ravi', 'Sita', 'Mohan'];
    const lastNames  = ['Kumar', 'Singh', 'Sharma', 'Gupta', 'Patel', 'Yadav', 'Mishra', 'Joshi', 'Verma'];
    const fatherNames = ['Ram Kumar', 'Shyam Singh', 'Vijay Sharma', 'Rakesh Gupta', 'Sunil Patel', 'Anil Yadav', 'Manoj Mishra', 'Dinesh Joshi'];
    const modes = ['Cash', 'Online Transfer', 'UPI', 'Cheque'];
    const rnd = arr => arr[Math.floor(Math.random() * arr.length)];

    const students = [];
    let serial = 1;
    classes.forEach(cls => {
      sections.forEach(sec => {
        for (let i = 1; i <= 4; i++) {
          students.push({
            id: `S${serial}`,
            serialNo: serial,
            name: `${rnd(firstNames)} ${rnd(lastNames)}`,
            fatherName: rnd(fatherNames),
            class: cls,
            section: sec,
            rollNo: i,
            phone: `9${Math.floor(100000000 + Math.random() * 899999999)}`,
            address: 'Village Demo, District Sample',
            admissionDate: '2026-04-01',
            createdAt: new Date().toISOString()
          });
          serial++;
        }
      });
    });
    this.saveStudents(students);

    const tuitionMap = { 'Nursery': 500, 'KG': 500, 'Class 1': 600, 'Class 2': 600, 'Class 3': 700, 'Class 4': 700, 'Class 5': 800 };
    const fees = [];
    let rcpNum = 1;

    students.slice(0, 30).forEach(student => {
      ['April', 'May'].forEach(month => {
        if (Math.random() > 0.25) {
          const tuition = tuitionMap[student.class] || 600;
          const reg     = month === 'April' ? 200 : 0;
          const misc    = 50;
          const dateDay = String(Math.floor(1 + Math.random() * 25)).padStart(2, '0');
          fees.push({
            id: `F${rcpNum}`,
            receiptNo: `RCP-2026-${String(rcpNum).padStart(4, '0')}`,
            studentId: student.id,
            session: '2026-2027',
            month,
            tuitionFee: tuition,
            registrationFee: reg,
            examFee: 0,
            miscFee: misc,
            total: tuition + reg + misc,
            paymentDate: `2026-0${month === 'April' ? '4' : '5'}-${dateDay}`,
            paymentMode: rnd(modes),
            transactionRef: '',
            remarks: '',
            createdAt: new Date().toISOString()
          });
          rcpNum++;
        }
      });
    });
    this.saveFees(fees);
    localStorage.setItem('fms_seeded', 'true');
  }
};
