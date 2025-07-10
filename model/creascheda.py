
from database.DAO import DAO

class Model:
    def __init__(self):


    def get_scheda_mensile(self, obiettivo, livello, frequenza, attrezzautura, muscolotarget ):
        esercizi = DAO.getEsercizi()





    def build_graph(self, year):
        self._grafo.clear()
        nodi = DAO.getNodi(year)
        if len(nodi) == 0:
            return
        self._grafo.add_nodes_from(nodi)
        for nodo in nodi:
            self._idMapPilota[int(nodo.driverId)] = nodo
        archi = DAO.getArchi(self._idMapPilota,year)
        for arch in archi:
            self._grafo.add_edge(arch[0], arch[1], weight=arch[2])

    def getGraphDetails(self):
        return self._grafo.number_of_nodes(), self._grafo.number_of_edges(), self.getBestdriver()

    def getBestdriver(self):
        bestdriver = None
        bestpunteggio = 0
        for n in self._grafo.nodes():
            scoreuscita = sum(self._grafo[n][succ]["weight"] for succ in self._grafo.successors(n))
            scoreentrata = sum(self._grafo[pred][n]["weight"] for pred in self._grafo.predecessors(n))
            score = scoreuscita- scoreentrata
            if score > bestpunteggio:
                bestpunteggio = score
                bestdriver = n
        return f"punteggio migliore: {bestpunteggio}; del guidatore ({bestdriver})"


    def getDreamTeam(self, soglia):
        self.bestSottoinsieme= set()
        self.bestTasso = float('inf')

        rimanenti = set(self._grafo.nodes())
        parziale = set()
        for n in list(rimanenti):
            parziale.add(n)
            rimanenti.remove(n)
            self.ricorsione(soglia, parziale, rimanenti)
            rimanenti.add(n)
            parziale.remove(n)
        return self.bestSottoinsieme, self.bestTasso


    def ricorsione(self,soglia, parziale, rimanenti):
        sconfitta = 0
        for u in rimanenti:
            for v in parziale:
                if self._grafo.has_edge(u, v):
                    sconfitta += self._grafo[u][v]['weight']

        if sconfitta >= self.bestTasso:
            return

        if len(parziale) == int(soglia):
            if sconfitta < self.bestTasso:
                self.bestTasso = sconfitta
                self.bestSottoinsieme = copy.deepcopy(parziale)
            return
        for nodo in list(rimanenti):  # oppure sorted(rimanenti)
            parziale.add(nodo)
            rimanenti.remove(nodo)
            self.ricorsione(soglia, parziale, rimanenti)
            parziale.remove(nodo)
            rimanenti.add(nodo)











    #tasso sconfitta è somma archi entranti da nodi esterni, quindi devo minimizzare somma archi entranti
