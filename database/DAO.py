from database.DB_connect import DBConnect

class DAO():

    @staticmethod
    def getEsercizi():
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary = True)

        query = """ select distinct year from formula1.seasons s """

        cursor.execute(query)

        results = []
        for row in cursor:
            results.append(row["year"])

        cursor.close()
        cnx.close()
        return results


