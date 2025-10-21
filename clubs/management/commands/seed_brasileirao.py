from typing import Dict, List

from django.core.management.base import BaseCommand
from django.db import transaction

from clubs.models import LeagueDivision, Team


class Command(BaseCommand):
    help = "Popula ligas (Séries A-D) e times do Campeonato Brasileiro, incluindo regiões/estados na Série D. Idempotente."

    # Mapeamento de estados para suas UFs (usado para desambiguar nomes duplicados na Série D)
    UF_MAP: Dict[str, str] = {
        # Norte
        "Acre": "AC",
        "Amapá": "AP",
        "Amazonas": "AM",
        "Pará": "PA",
        "Rondônia": "RO",
        "Roraima": "RR",
        "Tocantins": "TO",
        # Nordeste
        "Alagoas": "AL",
        "Bahia": "BA",
        "Ceará": "CE",
        "Maranhão": "MA",
        "Paraíba": "PB",
        "Pernambuco": "PE",
        "Piauí": "PI",
        "Rio Grande do Norte": "RN",
        "Sergipe": "SE",
        # Centro-Oeste
        "Distrito Federal": "DF",
        "Goiás": "GO",
        "Mato Grosso": "MT",
        "Mato Grosso do Sul": "MS",
        # Sudeste
        "Espírito Santo": "ES",
        "Minas Gerais": "MG",
        "Rio de Janeiro": "RJ",
        "São Paulo": "SP",
        # Sul
        "Paraná": "PR",
        "Rio Grande do Sul": "RS",
        "Santa Catarina": "SC",
    }

    SERIES_AB: Dict[str, List[str]] = {
        "Série A": [
            "Botafogo",
            "Palmeiras",
            "Flamengo",
            "São Paulo",
            "Cruzeiro",
            "Corinthians",
            "Vasco",
            "Atlético-MG",
            "Fluminense",
            "Red Bull Bragantino",
            "Santos",
            "Mirassol",
            "Bahia",
            "Ceará",
            "Fortaleza",
            "Sport",
            "Vitória",
            "Grêmio",
            "Internacional",
            "Juventude",
        ],
        "Série B": [
            "Athletico",
            "Coritiba",
            "Operário",
            "Criciúma",
            "Avaí",
            "Chapecoense",
            "América-MG",
            "Athletic",
            "Botafogo-SP",
            "Ferroviária",
            "Novorizontino",
            "Volta Redonda",
            "Cuiabá",
            "Atlético-GO",
            "Goiás",
            "Vila Nova",
            "Amazonas",
            "Paysandu",
            "Remo",
            "CRB",
        ],
        "Série C": [
            "Confiança",
            "Retrô",
            "Itabaiana",
            "Ferroviária FC",
            "Náutico",
            "ABC",
            "Botafogo-PB",
            "Floresta",
            "CSA",
            "Maringá",
            "Londrina",
            "Caxias",
            "Ypiranga",
            "Brusque",
            "Figueirense",
            "PontePreta",
            "Guarani",
            "Ituano",
            "Tombense",
            "São Bernardo",
            "Anápolis",
        ],
    }

    SERIE_D: Dict[str, Dict[str, List[str]]] = {
        "Norte": {
            "Acre": ["Humaitá", "Independência"],
            "Amapá": ["Trem"],
            "Amazonas": ["Manauara", "Manaus"],
            "Pará": ["Águia de Marabá", "Tuna Luso"],
            "Rondônia": ["Porto Velho"],
            "Roraima": ["GAS"],
            "Tocantins": ["União", "Tocantinópolis"],
        },
        "Nordeste": {
            "Alagoas": ["ASA", "Penedense"],
            "Bahia": ["Barcelona de Ilhéus", "Juazeirense", "Jequié"],
            "Ceará": ["Iguatu", "Maracanã", "Horizonte", "Ferroviário"],
            "Maranhão": ["Maranhão", "Imperatriz", "Sampaio Corrêa"],
            "Paraíba": ["Treze", "Sousa"],
            "Pernambuco": ["Central", "Santa Cruz"],
            "Piauí": ["Altos", "Parnahyba"],
            "Rio Grande do Norte": ["América", "Santa Cruz de Natal"],
            "Sergipe": ["Sergipe", "Lagarto"],
        },
        "Centro-Oeste": {
            "Distrito Federal": ["Capital", "Ceilândia"],
            "Goiás": ["Goianésia", "Goiatuba", "Goiânia", "Aparecidense"],
            "Mato Grosso": ["União Rondonópolis", "Luverdense"],
            "Mato Grosso do Sul": ["Operário"],
        },
        "Sudeste": {
            "Espírito Santo": ["Rio Branco", "Porto Vitória"],
            "Minas Gerais": ["Uberlândia", "Itabirito", "Pouso Alegre"],
            "Rio de Janeiro": ["Nova Iguaçu", "Boavista", "Maricá"],
            "São Paulo": ["Água Santa", "Inter de Limeira", "Portuguesa", "Monte Azul"],
        },
        "Sul": {
            "Paraná": ["Azuriz", "Cianorte", "Cascavel"],
            "Rio Grande do Sul": [
                "Guarany de Bagé",
                "Brasil de Pelotas",
                "São Luiz de Ijuí",
                "São José",
            ],
            "Santa Catarina": ["Marcílio Dias", "Joinville", "Barra"],
        },
    }

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING("Iniciando seed do Campeonato Brasileiro...")
        )

        serie_a = self._get_or_create_division(
            "Série A",
        )
        serie_b = self._get_or_create_division(
            "Série B",
            parent=serie_a,
        )
        serie_c = self._get_or_create_division(
            "Série C",
            parent=serie_b,
        )
        serie_d = self._get_or_create_division(
            "Série D",
            parent=serie_c,
        )

        # 2) Popula A, B, C
        self._seed_series(serie_a, "Série A")
        self._seed_series(serie_b, "Série B")
        self._seed_series(serie_c, "Série C")

        # 3) Popula Série D por regiões e estados
        self._seed_serie_d(serie_d)

        self.stdout.write(
            self.style.SUCCESS("Seed do Campeonato Brasileiro concluído com sucesso.")
        )

    def _get_or_create_division(
        self, name: str, parent: LeagueDivision | None = None
    ) -> LeagueDivision:
        obj, created = LeagueDivision.objects.get_or_create(
            name=name,
            defaults={"parent_league": parent},
        )
        if not created and parent and obj.parent_league_id != parent.id:
            # Garante hierarquia correta se já existir com outro parent
            obj.parent_league = parent
            obj.save(update_fields=["parent_league"])
        return obj

    def _seed_series(self, division: LeagueDivision, key: str) -> None:
        assert key in self.SERIES_AB
        self.stdout.write(self.style.NOTICE(f"Populando {key}..."))
        for team_name in self.SERIES_AB[key]:
            self._create_team_if_possible(team_name, division)

    def _seed_serie_d(self, serie_d: LeagueDivision) -> None:
        self.stdout.write(self.style.NOTICE("Populando Série D (regiões/estados)..."))

        for region, states in self.SERIE_D.items():
            region_div = self._get_or_create_division(region, parent=serie_d)

            for state, teams in states.items():
                state_div = self._get_or_create_division(state, parent=region_div)
                uf = self.UF_MAP.get(state)
                for team_name in teams:
                    self._create_team_if_possible(f"{team_name}-{uf}", state_div)

    def _create_team_if_possible(
        self, team_name: str, division: LeagueDivision, log_on_skip: bool = True
    ) -> bool:
        """Cria um Team se não existir outro com o mesmo nome em qualquer divisão.
        Retorna True se criou, False se já existia (neste caso não altera a divisão existente).
        """
        try:
            obj, created = Team.objects.get_or_create(
                name=team_name,
                defaults={"league_division": division},
            )
        except Exception as exc:  # proteção extra contra validações inesperadas
            self.stdout.write(
                self.style.WARNING(f"[WARN] Falha ao criar '{team_name}': {exc}")
            )
            return False

        if created:
            self.stdout.write(
                self.style.SUCCESS(f" [+] {team_name} -> {division.name}")
            )
            return True

        # Já existe um time com esse nome; mantém na divisão original
        if log_on_skip:
            self.stdout.write(
                self.style.WARNING(
                    f" [=] '{team_name}' já existe em '{obj.league_division.name}', mantendo e não duplicando."
                )
            )
        return False
