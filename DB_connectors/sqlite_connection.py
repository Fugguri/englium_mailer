import sqlite3

from models import UserClient,User

class Database:
    def __init__(self, db_file) -> None:

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def cbdt(self):
        with self.connection:
            create = """ CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE ON CONFLICT IGNORE,
                    full_name TEXT,
                    username TEXT,
                    has_access BOOLEAN DEFAULT FALSE 
                    );
                    CREATE TABLE IF NOT EXISTS clients
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INT,
                    api_id INT,
                    api_hash TEXT,
                    phone INTEGER NOT NULL UNIQUE ON CONFLICT IGNORE,
                    ai_settings TEXT,
                    mailing_text TEXT,
                    answers BIGINT DEFAULT 0,
                    gs TEXT UNIQUE ON CONFLICT IGNORE,
                    is_active BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY(user_id) REFERENCES users(id) )"""
            self.cursor.executescript(create)

    def add_user(self, user):
        with self.connection:
            self.cursor.execute(
            f"INSERT OR IGNORE INTO users( full_name, telegram_id, username) VALUES('{user.full_name}', '{user.id}', '{user.username}')")
    
    def create_client(self,user_id, phone, api_id, api_hash):
        with self.connection:
            self.cursor.execute(
            f"INSERT OR IGNORE INTO clients(user_id,phone, api_id, api_hash) VALUES((SELECT id FROM users WHERE telegram_id=? ),?,?,?)",(user_id, phone, api_id, api_hash))
            
    def get_user(self,telegram_id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("""SELECT id, telegram_id, username, full_name,has_access
                      FROM users
                      WHERE telegram_id=?""",
                      (telegram_id,))
            res = c.fetchone()
            user = User(*res)
            return user
    
            
    def get_client(self,id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT id, user_id, api_id, api_hash, phone, ai_settings, mailing_text,answers, gs,is_active FROM clients WHERE id=?",(id,))
            res = c.fetchone()
            user = UserClient(*res)
            return user
        
        
    def get_client_by_phone(self,phone):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT id, user_id, api_id, api_hash, phone, ai_settings, mailing_text,answers, gs,is_active FROM clients WHERE phone=?",(phone,))
            res = c.fetchone()
            user = UserClient(*res)
            return user
    
    def get_clients(self,user_id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT id,user_id,api_id,api_hash,phone,ai_settings,mailing_text,answers, gs,is_active FROM clients where user_id=?",(str(user_id)))
            res = c.fetchall()
            users = list()
            for re in res:
                re = list(map(lambda x:str(x),re))
                user = UserClient(*re)
                users.append(user)
            return users
            
    def get_active_clients(self):
        with self.connection:
            c = self.connection.cursor()
            c.execute("""SELECT c.id, c.user_id, c.api_id, c.api_hash, c.phone, c.ai_settings, c.mailing_text, c.answers, c.gs, c.is_active 
                           FROM clients as c
                           LEFT JOIN users as u on c.user_id=u.id
                           WHERE c.is_active=1 AND u.has_acces=1 """)
            res = c.fetchall()
            users = list()
            for re in res:
                user = UserClient(*re)
                users.append(user)
            return users
    
    def get_client_ai_settings(self,id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT ai_settings FROM clients where id=?",(id,))
            res = c.fetchone()
        return res
    
    def get_client_mailing_text(self,id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT mailing_text FROM clients where id=?",(id,))
            res = c.fetchone()
        return res
            
    def get_client_gs_name(self,id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT gs FROM clients where id=?",(id,))
            res = c.fetchone()
        return res
    
    def edit_client_gs(self,text, id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE clients SET gs=? WHERE id=?",(text,id,))
            self.connection.commit()
    
    def edit_client_mailing_text(self,text, id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE clients SET mailing_text=? WHERE id=?",(text,id,))
            self.connection.commit()
        
    def edit_client_ai_settings(self,text, id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE clients SET ai_settings=? WHERE id=?",(text,id,))
            self.connection.commit()
    
    def start_new_dialog_counter_update(self,phone):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE clients SET answers=answers+1 WHERE phone=?",(phone,))
            self.connection.commit()
            
    
            
    def update_all_clients(self,recepient_client_id, user_id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("""UPDATE clients 
                      SET 
                      mailing_text=(SELECT mailing_text FROM clients WHERE id=?),
                      ai_settings=(SELECT ai_settings FROM clients WHERE id=?)
                      WHERE user_id=?""",(recepient_client_id,recepient_client_id,user_id))
            self.connection.commit()
    
    
    
    def give_access(self,username):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE users SET has_access=? WHERE username=?",(True,username))
            self.connection.commit()
    
    def take_access(self,username):
        with self.connection:
            c = self.connection.cursor()
            c.execute("UPDATE users SET has_access=? WHERE username=?",(False,username))
            self.connection.commit()
    
    def delete_client(self,id):
        with self.connection:
            c = self.connection.cursor()
            c.execute("DELETE FROM clients WHERE id=?",(id))
            self.connection.commit()
            
if __name__ == "__main__":
    a = Database("FB.db")
    a.cbdt()
