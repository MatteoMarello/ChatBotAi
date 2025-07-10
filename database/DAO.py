from database.DB_connect import DBConnect



class DAO():

    @staticmethod
    def getAnni():
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
    def getNodi(year):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor()

        query = """ select  d.driverId,d.driverRef,d.number,d.code, d.forename,d.surname, d.dob, d.nationality, d.url
from formula1.races as ra, formula1.results as re, formula1.drivers d 
where ra.raceId = re.raceId and ra.year = "%s" and re.driverId = d.driverId 
and re.position IS NOT NULL"""

        cursor.execute(query, (year,))

        results = set()
        for row in cursor:
            results.add(Pilota(*row))

        cursor.close()
        cnx.close()
        return results

    @staticmethod
    def getArchi(_idMapPilota, year):
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """select r1.driverId as d1, r2.driverId as d2, count(*) as cnt
        				from results as r1, results as r2, races
        				where r1.raceId = r2.raceId
        				and races.raceId = r1.raceId
        				and races.year = %s
        				and r1.position is not null
        				and r2.position is not null 
        				and r1.position < r2.position 
        				group by d1, d2"""

        cursor.execute(query, (year,))

        for row in cursor:
            results.append((_idMapPilota[row["d1"]], _idMapPilota[row["d2"]], row["cnt"]))

        cursor.close()
        conn.close()
        return results

