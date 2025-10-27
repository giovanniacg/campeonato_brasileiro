from datetime import datetime, timedelta
from typing import List, Optional
from django.db import transaction
from django.utils import timezone
from matches.models import Match, Status
from leagues.models import LeagueDivision


class FixtureGeneratorService:
    DAYS_BETWEEN_MATCHES = 3
    MAX_MATCHES_PER_DAY = 5
    MATCH_TIME_SLOTS = ["16:00", "18:30", "21:00"]

    def __init__(
        self, league_division: LeagueDivision, start_date: Optional[datetime] = None
    ):
        self.league_division = league_division
        self.start_date = start_date or timezone.now() + timedelta(days=7)
        self.teams = list(league_division.teams.all())
        self.matches_created = []

    def generate_fixtures(self) -> List[Match]:
        if len(self.teams) < 2:
            raise ValueError("É necessário pelo menos 2 times para gerar confrontos.")

        with transaction.atomic():
            self._clear_existing_matches()
            round_robin_matches = self._generate_round_robin()
            self._schedule_matches(round_robin_matches)

        return self.matches_created

    def _clear_existing_matches(self):
        Match.objects.filter(
            league_division=self.league_division, status=Status.SCHEDULED
        ).delete()

    def _generate_round_robin(self) -> List[tuple]:
        teams = self.teams.copy()
        has_bye = len(teams) % 2 != 0
        if has_bye:
            teams.append(None)

        n = len(teams)
        first_leg = []

        cur = teams
        for round_num in range(n - 1):
            for i in range(n // 2):
                t1 = cur[i]
                t2 = cur[n - 1 - i]
                if t1 is None or t2 is None:
                    continue
                first_leg.append((t1, t2, round_num + 1))
            cur = [cur[0]] + [cur[-1]] + cur[1:-1]

        second_leg = [(a, h, r + (n - 1)) for (h, a, r) in first_leg]

        return first_leg + second_leg

    def _schedule_matches(self, round_robin_matches: List[tuple]):
        REST_DAYS = self.DAYS_BETWEEN_MATCHES
        MAX_PER_DAY = self.MAX_MATCHES_PER_DAY
        SLOTS = self.MATCH_TIME_SLOTS

        start_dt = self.start_date
        current_day = start_dt.date()

        last_play_dt = {}
        remaining = list(round_robin_matches)

        while remaining:
            matches_today = 0
            teams_used_today = set()

            daily_slots = []
            if current_day == start_dt.date():
                for s in SLOTS:
                    h, m = map(int, s.split(":"))
                    slot_dt = timezone.make_aware(
                        datetime(
                            current_day.year,
                            current_day.month,
                            current_day.day,
                            h,
                            m,
                            0,
                        )
                    )
                    if slot_dt >= start_dt:
                        daily_slots.append((s, slot_dt))
            else:
                for s in SLOTS:
                    h, m = map(int, s.split(":"))
                    slot_dt = timezone.make_aware(
                        datetime(
                            current_day.year,
                            current_day.month,
                            current_day.day,
                            h,
                            m,
                            0,
                        )
                    )
                    daily_slots.append((s, slot_dt))

            if not daily_slots:
                current_day += timedelta(days=1)
                continue

            for i in range(len(remaining) - 1, -1, -1):
                if matches_today >= MAX_PER_DAY or not daily_slots:
                    break

                home_team, away_team, _round = remaining[i]
                h_id, a_id = home_team.id, away_team.id

                if h_id in teams_used_today or a_id in teams_used_today:
                    continue

                slot_str, slot_dt = daily_slots[0]

                h_last = last_play_dt.get(h_id)
                a_last = last_play_dt.get(a_id)
                if h_last is not None and (slot_dt - h_last) < timedelta(
                    days=REST_DAYS
                ):
                    continue
                if a_last is not None and (slot_dt - a_last) < timedelta(
                    days=REST_DAYS
                ):
                    continue

                daily_slots.pop(0)

                match = Match.objects.create(
                    home_team=home_team,
                    away_team=away_team,
                    league_division=self.league_division,
                    date=slot_dt,
                    status=Status.SCHEDULED,
                )

                self.matches_created.append(match)
                last_play_dt[h_id] = slot_dt
                last_play_dt[a_id] = slot_dt
                teams_used_today.update((h_id, a_id))
                remaining.pop(i)
                matches_today += 1

            current_day += timedelta(days=1)
