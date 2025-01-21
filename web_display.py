from flask import Flask, render_template, request
from schedule import Schedule
import calendar

app = Flask(__name__)

class WebDisplay:
    def __init__(self, schedule):
        self.schedule = schedule
        self.days_fr = {
            'm': 'Lundi',
            'tu': 'Mardi',
            'w': 'Mercredi',
            'th': 'Jeudi',
            'f': 'Vendredi'
        }

    def format_time(self, minutes: int) -> str:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def get_schedule_data(self, tutor_filter=None, room_filter=None, group_filter=None):
        schedule_grid = {day: {time: [] for time in self.schedule.time_slots} 
                        for day in self.schedule.days}
        
        for course in self.schedule.courses:
            # Ignorer les cours avec des données manquantes
            if not course.tutor or not course.room or not course.room.name:
                continue
                
            # Appliquer les filtres
            if tutor_filter and course.tutor != tutor_filter:
                continue
            if room_filter and course.room.name != room_filter:
                continue
            if group_filter:
                group_found = False
                for group in course.groups:
                    if group.name == group_filter:
                        group_found = True
                        break
                if not group_found:
                    continue
                
            try:
                schedule_grid[course.day][course.start_time].append({
                    'module': course.module.abbrev if course.module else "N/A",
                    'tutor': course.tutor,
                    'room': course.room.name,
                    'type': course.type if course.type else "N/A",
                    'groups': [g.name for g in course.groups],
                    'color_bg': course.module.color_bg if course.module else "#FFFFFF",
                    'color_txt': course.module.color_txt if course.module else "#000000"
                })
            except (AttributeError, KeyError):
                # Ignorer les cours avec des données invalides
                continue
            
        return schedule_grid

    def get_filter_options(self):
        # Récupérer tous les tuteurs
        tutors = []
        for course in self.schedule.courses:
            if course.tutor:  # Si le tuteur n'est pas None
                tutors.append(course.tutor)
        tutors = sorted(set(tutors))  # Trier la liste des tuteurs uniques
        
        # Récupérer toutes les salles
        rooms = []
        for course in self.schedule.courses:
            if course.room and course.room.name:  # Si la salle et son nom ne sont pas None
                rooms.append(course.room.name)
        rooms = sorted(set(rooms))  # Trier la liste des salles uniques
        
        # Récupérer tous les groupes
        groups = []
        for course in self.schedule.courses:
            for group in course.groups:
                if group.name:  # Si le nom du groupe n'est pas None
                    groups.append(group.name)
        groups = sorted(set(groups))  # Trier la liste des groupes uniques
        
        return tutors, rooms, groups

@app.route('/')
def display_schedule():
    schedule = Schedule()
    schedule.load_data('json/cours.json', 'disponibilites')
    schedule.generate_schedule()
    
    web_display = WebDisplay(schedule)
    
    # Récupérer les filtres depuis les paramètres URL
    tutor_filter = request.args.get('tutor')
    room_filter = request.args.get('room')
    group_filter = request.args.get('group')
    
    # Récupérer les options de filtres
    tutors, rooms, groups = web_display.get_filter_options()
    
    schedule_data = web_display.get_schedule_data(tutor_filter, room_filter, group_filter)
    
    time_slots = [(slot, web_display.format_time(slot)) 
                 for slot in schedule.time_slots]
    
    return render_template(
        'schedule.html',
        days=schedule.days,
        days_fr=web_display.days_fr,
        time_slots=time_slots,
        schedule_data=schedule_data,
        tutors=tutors,
        rooms=rooms,
        groups=groups,
        selected_tutor=tutor_filter,
        selected_room=room_filter,
        selected_group=group_filter
    )

if __name__ == '__main__':
    app.run(debug=True) 