import sqlite3

conn = sqlite3.connect("baza.db")
cursor = conn.cursor()

# Brišemo podatke iz svih tabela
cursor.execute("DELETE FROM datumi")
cursor.execute("DELETE FROM lokacije")
cursor.execute("DELETE FROM kompanije")

conn.commit()
conn.close()

uspjeh = "Baza je uspješno očišćena i ispražnjena!"
print(uspjeh)