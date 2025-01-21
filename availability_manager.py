from dataclasses import dataclass
from typing import Dict, List
import json
import os

@dataclass
class TeacherAvailability:
    username: str
    week: int
    year: int
    availabilities: Dict[str, List[int]]
    
class AvailabilityManager:
    def __init__(self):
        self.teachers_availability = {}
        
    def load_availabilities(self, directory: str):
        """Charge les disponibilités de tous les enseignants depuis un répertoire"""
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                teacher = filename.replace('.json', '')
                filepath = os.path.join(directory, filename)
                
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                # Structure attendue des disponibilités par jour
                availabilities = {
                    'm': [],  # Lundi
                    'tu': [], # Mardi
                    'w': [],  # Mercredi
                    'th': [], # Jeudi
                    'f': []   # Vendredi
                }
                
                # Traitement des disponibilités
                if 'availabilities' in data:
                    for day_data in data['availabilities']:
                        day = day_data.get('day', '').lower()
                        if day in availabilities:
                            start_time = day_data.get('start_time')
                            if start_time is not None:
                                availabilities[day].append(start_time)
                
                # Création de l'objet TeacherAvailability
                teacher_avail = TeacherAvailability(
                    username=teacher,
                    week=data.get('week', 0),
                    year=data.get('year', 0),
                    availabilities=availabilities
                )
                
                self.teachers_availability[teacher] = teacher_avail
    
    def is_teacher_available(self, teacher: str, day: str, time_slot: int) -> bool:
        """Vérifie si un enseignant est disponible à un créneau donné"""
        if teacher not in self.teachers_availability:
            return True  # Si pas d'info, on suppose disponible
            
        teacher_avail = self.teachers_availability[teacher]
        if day not in teacher_avail.availabilities:
            return True
            
        # Si le créneau est dans la liste des disponibilités
        return time_slot in teacher_avail.availabilities[day]
