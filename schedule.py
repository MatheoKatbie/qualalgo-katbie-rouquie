from dataclasses import dataclass
from typing import List, Dict
import json
from datetime import datetime, time
import random
from availability_manager import AvailabilityManager

@dataclass
class Room:
    id: int
    name: str
    room_type: str

@dataclass 
class Group:
    id: int
    train_prog: str
    name: str
    is_structural: bool

@dataclass
class Module:
    name: str
    abbrev: str
    color_bg: str
    color_txt: str

@dataclass
class Course:
    id: int
    type: str
    room_type: str
    week: int
    year: int
    groups: List[Group]
    module: Module
    tutor: str
    start_time: int
    room: Room
    day: str
    
class TimeSlot:
    def __init__(self, day: str, start_time: int):
        self.day = day
        self.start_time = start_time
        
    def __eq__(self, other):
        return self.day == other.day and self.start_time == other.start_time

class Schedule:
    def __init__(self):
        self.courses = []
        self.days = ['m', 'tu', 'w', 'th', 'f']
        self.time_slots = [480, 570, 665, 755, 855, 945, 1040]
        self.availability_manager = AvailabilityManager()
        
    def load_data(self, courses_file: str, availabilities_dir: str):
        """Charge les données des cours et des disponibilités"""
        # Chargement des cours
        with open(courses_file, 'r') as f:
            data = json.load(f)
            
        for course_data in data:
            room = Room(
                course_data['room']['id'],
                course_data['room']['name'],
                course_data.get('room_type', '')
            )
            
            groups = [Group(**g) for g in course_data['course']['groups']]
            
            module = Module(
                course_data['course']['module']['name'],
                course_data['course']['module']['abbrev'],
                course_data['course']['module']['display']['color_bg'],
                course_data['course']['module']['display']['color_txt']
            )
            
            course = Course(
                course_data['id'],
                course_data['course']['type'],
                course_data['course']['room_type'],
                course_data['course']['week'],
                course_data['course']['year'],
                groups,
                module,
                course_data['tutor'],
                course_data['start_time'],
                room,
                course_data['day']
            )
            
            self.courses.append(course)
            
        # Chargement des disponibilités
        self.availability_manager.load_availabilities(availabilities_dir)

    def check_conflicts(self, course: Course, time_slot: TimeSlot) -> bool:
        """Vérifie les conflits et les contraintes horaires"""
        
        # Pas de cours entre 12h et 13h (720-780 minutes)
        if 720 <= time_slot.start_time < 780:
            return True
        
        # Pas de cours le vendredi après 15h40 (940 minutes), sauf si déjà planifié
        if time_slot.day == 'f' and time_slot.start_time >= 940:
            # Vérifie si c'est un cours existant déjà planifié
            for existing_course in self.courses:
                if (existing_course.day == 'f' and 
                    existing_course.start_time >= 940 and 
                    existing_course.id == course.id):
                    return False  # Permet le cours existant
            return True  # Bloque les nouveaux cours
        
        # Vérifie les disponibilités de l'enseignant
        if not self.availability_manager.is_teacher_available(
            course.tutor, 
            time_slot.day, 
            time_slot.start_time
        ):
            return True
        
        # Vérifie les conflits avec les autres cours
        for existing_course in self.courses:
            if existing_course.day == time_slot.day and existing_course.start_time == time_slot.start_time:
                # Conflit de professeur
                if existing_course.tutor == course.tutor:
                    return True
                    
                # Conflit de groupe
                for group1 in existing_course.groups:
                    for group2 in course.groups:
                        if group1.id == group2.id:
                            return True
                            
                # Conflit de salle
                if existing_course.room.id == course.room.id:
                    return True
                    
        return False

    def generate_schedule(self):
        unscheduled_courses = self.courses.copy()
        scheduled_courses = []
        
        # Trie les cours par contraintes (CM en premier, etc.)
        unscheduled_courses.sort(key=lambda x: x.type == 'CM', reverse=True)
        
        for course in unscheduled_courses:
            placed = False
            
            # Essaie tous les créneaux possibles
            for day in self.days:
                for start_time in self.time_slots:
                    # Vérifie les contraintes spécifiques
                    if start_time == 1040 and course.type == 'CM':  # Pas de CM à 17h10
                        continue
                        
                    time_slot = TimeSlot(day, start_time)
                    
                    if not self.check_conflicts(course, time_slot):
                        course.day = day
                        course.start_time = start_time
                        scheduled_courses.append(course)
                        placed = True
                        break
                        
                if placed:
                    break
                    
            if not placed:
                print(f"Impossible de placer le cours {course.module.name}")
                
        return scheduled_courses

    def display_schedule(self):
        # Crée un dictionnaire pour organiser les cours par jour et créneau
        schedule_grid = {day: {time: [] for time in self.time_slots} for day in self.days}
        
        for course in self.courses:
            schedule_grid[course.day][course.start_time].append(course)
            
        # Affiche l'emploi du temps
        print("\nEmploi du temps:")
        print("=" * 100)
        
        # En-tête des jours
        days_fr = {'m': 'Lundi', 'tu': 'Mardi', 'w': 'Mercredi', 'th': 'Jeudi', 'f': 'Vendredi'}
        print(f"{'Horaire':12}", end='')
        for day in self.days:
            print(f"{days_fr[day]:20}", end='')
        print()
        print("-" * 100)
        
        # Contenu
        for time_slot in self.time_slots:
            print(f"{self.format_time(time_slot):12}", end='')
            for day in self.days:
                courses = schedule_grid[day][time_slot]
                if courses:
                    course = courses[0]  # Prend le premier cours s'il y en a plusieurs
                    print(f"{course.module.abbrev[:15]:20}", end='')
                else:
                    print(f"{'':20}", end='')
            print()

    @staticmethod
    def format_time(minutes: int) -> str:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

def main():
    schedule = Schedule()
    schedule.load_data('json/cours.json', 'data/disponibilites')
    schedule.generate_schedule()
    schedule.display_schedule()

if __name__ == "__main__":
    main()
