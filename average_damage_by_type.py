import json
from statistics import mean

from mrjob.job import MRJob
from mrjob.step import MRStep


class AverageDamageByType(MRJob):
    def steps(self):
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]

    def mapper(self, _, line):
        pokemon_detail = json.loads(line)
        all_damages = [
            (key, value)
            for key, value in pokemon_detail.items()
            if key.startswith("Damage_by")
        ]
        for damage in all_damages:
            damage_name = damage[0]
            damage_value = damage[1]
            yield (damage_name, damage_value)

    def reducer(self, key, value):
        yield (key, mean(value))


if __name__ == "__main__":
    AverageDamageByType.run()
