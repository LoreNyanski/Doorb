from datetime import datetime, timedelta

from .interface_db import add_incident

class Incident:
    """A class that represents a single incident of someone pushing on a pull door (or vice versa)"""

    def __init__(self, dumbass_id: int, occurance: datetime):
        self.dumbass_id = dumbass_id
        self.occurance = occurance

    @staticmethod
    def parser(row) -> Incident:
        """Takes a row from the incidents table and returns it as an incident"""
        dont_care, dumbass_id, occurance = row
        occurance = datetime.fromisoformat(occurance)
        return Incident(dumbass_id, occurance)

    def save(self):
        """Saves the incident to the database"""
        ser_occurance = self.occurance.isoformat()
        add_incident(self.dumbass_id, ser_occurance)

    def __sub__(self, other):
        if not isinstance(other, Incident):
            raise NotImplementedError
        else:
            return IncidentInterval(self.occurance, other.occurance)

class IncidentInterval:

    def __init__(self, end_time: datetime, start_time: datetime):
        if start_time > end_time:
            raise ValueError("start_time can't be after end_time")
        self.end_time = end_time
        self.start_time = start_time
        self.length = end_time - start_time

    def __len__(self) -> timedelta:
        return self.length

    def __lt__(self, other):
        if not isinstance(other, IncidentInterval):
            raise NotImplementedError
        else:
            return self.length < other.length
        
    def __eq__(self, other):
        if not isinstance(other, IncidentInterval):
            raise NotImplementedError
        else:
            return self.length == other.length
        
    def __gt__(self, other):
        if not isinstance(other, IncidentInterval):
            raise NotImplementedError
        else:
            return self.length > other.length