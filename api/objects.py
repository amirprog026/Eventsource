from dataclasses import dataclass,asdict,field
import json
from typing import Any
def getChange_percent(p1,p2):
    """compare p1 to p2"""
    percent=(p1-p2)/100 
    return percent
@dataclass
class EventModel:
    eventid:int
    eventtype :str #order,action,entrance,...
    source :str
    user:str
    occured_at :str
    metadata = dict
    def __json__(self) -> str:
        """
        dataclass instance to a JSON string.
        """
        # Convert the dataclass to a dictionary
        data_dict = asdict(self)
        # Serialize to a JSON string
        return json.dumps(data_dict, ensure_ascii=False, indent=4)

@dataclass
class DailyEvent:
    overalsale:int
    overaluser:int
    totalevents:int
    def calculate_changes(self,Eventpack):
        total=getChange_percent(int(self.totalevents),int(Eventpack.totalevents))
        salescount=getChange_percent(int(self.overalsale),int(Eventpack.overalsale))
        usercount=getChange_percent(int(self.overaluser),int(Eventpack.overaluser))
        
        return {"totalevents":total,
                "sales":salescount,
                "usercount":usercount
                }
    