import sqlite3


class Database():
    def __init__(self, dataset):
        self.conn = sqlite3.connect(dataset)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
                  CREATE TABLE IF NOT EXISTS data
                  (plate_owner, license_plate)
                  ''')


    def show_plates(self):
        result=self.cursor.execute('SELECT * FROM data')
        plates=result.fetchall()
        return plates


    def add_new(self, plate_owner, license_plate):
        if self.cursor.execute(f"SELECT 1 FROM data WHERE license_plate = '{license_plate}'").fetchone() == None:
            self.cursor.execute(f"INSERT INTO data VALUES('{plate_owner}', '{license_plate}')")
            self.conn.commit()
            print('Added successfully.')
        else:
            print('This Plate has already added!')

    
    def remove(self):
        remove_way = input('Remove with plate_owner(O) or license_plate(P)? O/P : ')

        if remove_way == 'O':
            plate = input('PLease enter plate_owner : ')
            self.remove_owner(plate)
        elif remove_way == 'P':
            plate = input('PLease enter license_plate : ')
            self.remove_plate(plate)
        else:
            print('Please just enter O(plate_owner) or P(license_plate)')
            self.show_plates()
            self.remove()


    def remove_owner(self, owner):
        self.cursor.execute(f'DELETE FROM data WHERE plate_owner="{owner}"')
        self.conn.commit()
        print('Plate(s) deleted successfully.')


    def remove_plate(self, plate):
        self.cursor.execute(f'DELETE FROM data WHERE license_plate="{plate}"')
        self.conn.commit()
        print('Plate deleted successfully.')




if __name__ == "__main__":
    database = Database()

    plates = database.show_plates()
    print(plates)

    database.add_new('person1', '67e95442')

    database.remove()