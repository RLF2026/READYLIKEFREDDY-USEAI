"""RLF SUPPLIER ENGINE — proves del motor.

Proven les regles amb textos sintetics DINS del test i comproven que el motor
REBUTJA el que no te font. Es demostrar que el motor no deixa entrar cap dada
inventada.
"""
import unittest

from supplier_engine import (
    Classificacio, EntradaProveidor, EstatVerificacio, Evidencia,
    MotorProveidors, any_de_la_linia, anys_en_text, clau_canonica,
    es_preloved, marques_en_text, te_evidencia_suficient,
)


def entrada(**over):
    base = dict(nom="Botiga Exemple", localitat="Ciutat", sector="Sector 1", pais="Alemanya", url="https://exemple.test", font="font-exemple", data_consulta="2026-09-26")
    base.update(over)
    return EntradaProveidor(**base)


def evid(text="Aquesta botiga ven roba vintage i fred perry de segona ma des de 1975.", tipus="cataleg"):
    return Evidencia(tipus=tipus, url="https://exemple.test/cataleg", data_consulta="2026-09-26", extracte=text)


class TestNormalitzacio(unittest.TestCase):
    def test_clau_ignora_accents_i_majuscules(self):
        self.assertEqual(clau_canonica("Botiga Munich", "Munchen", "Alemanya"), clau_canonica("botiga munich", "munchen", "alemanya"))

    def test_clau_distingeix_localitats(self):
        self.assertNotEqual(clau_canonica("Botiga", "Berlin", "Alemanya"), clau_canonica("Botiga", "Hamburg", "Alemanya"))


class TestDeteccions(unittest.TestCase):
    def test_marques_britaniques(self):
        self.assertIn("fred perry", marques_en_text("Venem Fred Perry i Ben Sherman"))
        self.assertIn("ben sherman", marques_en_text("Venem Fred Perry i Ben Sherman"))

    def test_preloved(self):
        self.assertTrue(es_preloved("roba de segona ma"))
        self.assertTrue(es_preloved("Preloved London"))
        self.assertFalse(es_preloved("botiga nova de roba"))

    def test_anys_en_text(self):
        self.assertEqual(anys_en_text("establert el 1975 a Londres"), [1975])
        self.assertEqual(sorted(anys_en_text("peca de 1968 i una altra de 1994")), [1968, 1994])
        self.assertEqual(anys_en_text("sense anys"), [])

    def test_finestra_temporal(self):
        self.assertTrue(any_de_la_linia(1952))
        self.assertTrue(any_de_la_linia(2026))
        self.assertFalse(any_de_la_linia(1951))
        self.assertFalse(any_de_la_linia(2030))

    def test_evidencia_minima(self):
        self.assertTrue(te_evidencia_suficient([evid()]))
        self.assertFalse(te_evidencia_suficient([]))
        self.assertFalse(te_evidencia_suficient([evid("curt")]))


class TestMotor(unittest.TestCase):
    def setUp(self):
        self.motor = MotorProveidors()

    def test_registra_amb_evidencia_valida(self):
        p = self.motor.processa(entrada(), [evid()])
        self.assertEqual(p.estat, EstatVerificacio.VERIFICAT)
        self.assertEqual(self.motor.total(), 1)

    def test_rebutja_sense_evidencia(self):
        p = self.motor.processa(entrada(), [])
        self.assertEqual(p.estat, EstatVerificacio.REBUTJAT)
        self.assertEqual(self.motor.total(), 0)
        self.assertIn("SENSE_FONT", p.motius[0])

    def test_rebutja_camps_buits(self):
        p = self.motor.processa(entrada(nom=""), [evid()])
        self.assertEqual(p.estat, EstatVerificacio.REBUTJAT)
        self.assertIn("DADES_INCOMPLETES", p.motius[0])

    def test_rebutja_url_no_valida(self):
        p = self.motor.processa(entrada(url="no-es-una-url"), [evid()])
        self.assertEqual(p.estat, EstatVerificacio.REBUTJAT)
        self.assertIn("SENSE_URL", p.motius[0])

    def test_rebutja_duplicat(self):
        e = entrada()
        self.motor.processa(e, [evid()])
        p2 = self.motor.processa(e, [evid()])
        self.assertEqual(p2.estat, EstatVerificacio.REBUTJAT)
        self.assertIn("DUPLICAT", p2.motius[0])
        self.assertEqual(self.motor.total(), 1)

    def test_rebutja_fora_temporal(self):
        p = self.motor.processa(entrada(), [evid("Colleccio de peces del 1930 i 1935.")])
        self.assertEqual(p.estat, EstatVerificacio.REBUTJAT)
        self.assertIn("FORA_TEMPORAL", p.motius[0])

    def test_rebutja_no_preloved(self):
        p = self.motor.processa(entrada(), [evid("Botiga de roba nova d'esport per a nens i nenes.")])
        self.assertEqual(p.estat, EstatVerificacio.REBUTJAT)
        self.assertIn("NO_ES_BOTIGA_PRELOVED", p.motius[0])

    def test_classifica_especialista(self):
        p = self.motor.processa(entrada(), [evid("Som Fred Perry Specialist des de 1960, fred perry only.")])
        self.assertEqual(p.classificacio, Classificacio.ESPECIALISTA_FRED_PERRY)

    def test_classifica_marques_britaniques(self):
        p = self.motor.processa(entrada(), [evid("Especialistes en Baracuta i Burberry vintage.")])
        self.assertEqual(p.classificacio, Classificacio.MARQUES_BRITANIQUES)

    def test_classifica_segona_ma(self):
        p = self.motor.processa(entrada(nom="Altres"), [evid("Botiga de segona ma generalista, consignment i thrift.")])
        self.assertEqual(p.classificacio, Classificacio.SEGONA_MA_FOCALITZADA)

    def test_progres_i_export(self):
        self.motor.processa(entrada(), [evid()])
        prog = self.motor.progres_objectiu()
        self.assertEqual(prog["registrats"], 1)
        self.assertEqual(prog["objectiu"], 10000)
        exp = self.motor.exporta()
        self.assertEqual(len(exp["proveidors"]), 1)
        self.assertTrue(exp["empremta"])

    def test_determinisme(self):
        m1 = MotorProveidors()
        m2 = MotorProveidors()
        m1.processa(entrada(), [evid()])
        m2.processa(entrada(), [evid()])
        self.assertEqual(m1.exporta()["empremta"], m2.exporta()["empremta"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
