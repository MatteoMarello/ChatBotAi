from database.DB_connect import DBConnect
from model.esercizio import Esercizio

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

    @staticmethod
    def getEsercizi(context, muscolo):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary = True)

        query = """select e.*
from fitness_db.exercises e, fitness_db.contexts c, fitness_db.exercise_context_priority ecp 
where c.nome = %s and c.id = ecp.context_id and e.muscolo_primario = %s 
and ecp.exercise_id = e.id and ecp.priority_level <> 99
order by ecp.priority_level asc
"""

        cursor.execute(query,(context,muscolo))

        results = []
        for row in cursor:
            results.append(Esercizio(**row))

        cursor.close()
        cnx.close()
        return results

if __name__ == '__main__':
    myDAO = DAO()
    print(myDAO.getEsercizi("Home Manubri","Bicipiti"))


