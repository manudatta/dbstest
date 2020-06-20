data = [
("username1","phone_number1", "email1"),
("usernameX","phone_number1", "emailX"),
("usernameZ","phone_numberZ", "email1Z"),
("usernameY","phone_numberY", "emailX"),
]

class Aggregator(object):
    def __init__(self, count):
        self._bucket_count = 0
        self._value_dicts = [{} for _ in range(count)]
        self._indices = []
        self._call_count = -1

    def add(self, datum):
        """ keep index for each col in tuple """
        self._call_count += 1
        match, bucket = False, None
        for attr, d in zip(datum,self._value_dicts):
            bucket = d.get(attr)
            if bucket is not None:
                self._indices[bucket].append(self._call_count)
                match = True
                break
        if not match:
            bucket = self._bucket_count
            self._bucket_count += 1
            self._indices.append([self._call_count])
        for attr, d in zip(datum, self._value_dicts):
            d[attr] = bucket
        return self._bucket_count-1

    @property
    def indices(self):
        return self._indices

agg = Aggregator(3)
for datum in data:
    agg.add(datum)
print(agg.indices)
