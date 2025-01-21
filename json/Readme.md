# API FlopEDT

https://flopedt.iut-blagnac.fr/fr/api/doc/

# Cours

curl 'https://flopedt.iut-blagnac.fr/fr/api/fetch/scheduledcourses/?week=4&year=2025&dept=INFO'

# Disponibilités des intervenants

cat cours.json | grep '"tutor'  | sort |  uniq | awk '{print $2}' | cut -d'"' -f2 | while read tutor; do curl "https://flopedt.iut-blagnac.fr/fr/api/preferences/user-actual/?dept=INFO&week=4&year=2025&user=$tutor" > disponibilites/$tutor.json; done

# Rooms et type

curl https://flopedt.iut-blagnac.fr/fr/api/rooms/all/?dept=INFO > rooms.json


## Astuce pretty print

apt install -y jq
cat xxx.json | jq . | less
