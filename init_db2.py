import sqlite3

# Connect to your CKD database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insert multiple doctors
cursor.executescript("""
INSERT INTO doctors (name, specialty, city, hospital, contact) VALUES
('Dr. Rajesh Kumar', 'Nephrologist', 'Bangalore', 'Apollo Hospitals', 'rajesh.kumar@apollohospitals.com'),
('Dr. Anita Desai', 'Nephrologist', 'Mumbai', 'Lilavati Hospital', 'anita.desai@lilavatihospital.com'),
('Dr. Suresh Reddy', 'Nephrologist', 'Hyderabad', 'Yashoda Hospitals', 'suresh.reddy@yashodahospitals.com'),
('Dr. Priya Sharma', 'Nephrologist', 'Delhi', 'Max Healthcare', 'priya.sharma@maxhealthcare.com'),
('Dr. Arvind Nair', 'Nephrologist', 'Chennai', 'MIOT Hospitals', 'arvind.nair@miot.in'),
('Dr. Kavita Mehra', 'Nephrologist', 'Pune', 'Jehangir Hospital', 'kavita.mehra@jehangirhospital.com'),
('Dr. Manoj Gupta', 'Nephrologist', 'Kolkata', 'Fortis Hospital', 'manoj.gupta@fortishospitals.com'),
('Dr. Sneha Iyer', 'Nephrologist', 'Ahmedabad', 'CIMS Hospital', 'sneha.iyer@cims.org'),
('Dr. Vikram Joshi', 'Nephrologist', 'Bangalore', 'Manipal Hospitals', 'vikram.joshi@manipalhospitals.com'),
('Dr. Meena Das', 'Nephrologist', 'Mumbai', 'Nanavati Hospital', 'meena.das@nanavatihospital.com');
""")

# Save (commit) the changes
conn.commit()

# Close the connection
conn.close()

print("✅ Doctors inserted successfully into the 'doctors' table!")