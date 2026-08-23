import sqlite3

# Ime baze mora biti ono koje koristiš u aplikaciji
conn = sqlite3.connect("znr_baza.db")
cursor = conn.cursor()

# Brišemo podatke iz svih tabela prema trenutnoj šemi
cursor.execute("DELETE FROM masine")
cursor.execute("DELETE FROM obuke")
cursor.execute("DELETE FROM ljekarski")
cursor.execute("DELETE FROM rizicna_mjesta")
cursor.execute("DELETE FROM opasne_materije")
cursor.execute("DELETE FROM lzo")
cursor.execute("DELETE FROM posude_pod_pritiskom")
cursor.execute("DELETE FROM povrede_na_radu")

# Ako želiš da očistiš i podatke firme iz tabele korisnika (da vratiš na prazno):
cursor.execute("UPDATE korisnici SET podaci_firme = '{}'")

conn.commit()
conn.close()

print("Baza 'znr_baza.db' je uspješno očišćena i ispražnjena!")