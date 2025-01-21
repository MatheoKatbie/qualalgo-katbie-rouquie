import os
from schedule import Schedule


def main():
    # Création des répertoires nécessaires
    if not os.path.exists('disponibilites'):
        os.makedirs('disponibilites')
        
    schedule = Schedule()
    
    schedule.load_data(
        courses_file='json/cours.json',
        availabilities_dir='disponibilites'
    )
    
    schedule.generate_schedule()
    schedule.display_schedule()

if __name__ == "__main__":
    main()