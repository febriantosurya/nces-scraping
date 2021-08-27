from fuzzywuzzy import process
from os import listdir


class WantedSchool:
  def __init__(self, row):
    self.title = row[0]
    self.lat = row[1]
    self.long = row[2]
    self.state = row[4]
    self.is_private = True if row[5] == 'TRUE' else False
    self.nces = ''


  def print_wanted_school(self):
    str_format = '{0} {1}'.format(self.title, self.nces)
    print(str_format)


  @staticmethod
  def get_wanted_schools(WANTED_SCHOOL_FILE):
    with open(WANTED_SCHOOL_FILE, 'r') as file:
      lines = file.readlines()
      wanted_schools = []
      for line in lines:
        row = line.split(',')
        wanted_school = WantedSchool(row)
        wanted_schools.append(wanted_school)
      return wanted_schools


class NCESSchool:
  def __init__(self, row, is_private):
    try:
      self.title = row[1] if is_private else row[6]
      self.state = row[8] if is_private else row[11]
      self.nces = row[0] if is_private else row[0]
    except Exception as e:
      print('[SKIP] Finding {0}'.format(row))
      self.title = -1

  
  @staticmethod
  def get_nces_schools(NCES_SCHOOL_FILE, is_private):
    with open(NCES_SCHOOL_FILE, 'r') as file:
      lines = file.readlines()
      nces_schools = []

      if is_private:
        for line in lines:
          row = line.split(',')
          nces_school = NCESSchool(row, is_private)
          if nces_school.title != -1:
            nces_schools.append(nces_school)
      else:
        for line in lines:
          row = line.split(';')
          nces_school = NCESSchool(row, is_private)
          if nces_school.title != -1:
            nces_schools.append(nces_school)

      return nces_schools


  @staticmethod
  def get_nces_school_titles_from_nces_schools(nces_schools):
    nces_school_titles = []
    for nces_school in nces_schools:
      nces_school_titles.append(nces_school.title)
    return nces_school_titles


  @staticmethod
  def get_nces_school_from_nces_schools(nces_school_title, nces_schools):
    for nces_school in nces_schools:
      if nces_school.title == nces_school_title:
        return nces_school
    return None


def load_all_nces_schools(NCES_SCHOOL_DIR, is_private):
  all_nces_schools = {}
  filenames = listdir(NCES_SCHOOL_DIR)
  for filename in filenames:
    if '.csv' in filename:
      state = filename.split('.')[0]
      filename = '{0}/{1}'.format(NCES_SCHOOL_DIR, filename)
      nces_schools = NCESSchool.get_nces_schools(filename, is_private)
      all_nces_schools[state] = nces_schools
  return all_nces_schools


def fill_nces_of_wanted_school(wanted_school, nces_schools):
  most_relevant_nces_school = get_most_relevant_nces_school_with_wanted_school(wanted_school, nces_schools)
  wanted_school.nces = most_relevant_nces_school.nces
  return wanted_school, most_relevant_nces_school


def get_most_relevant_nces_school_with_wanted_school(wanted_school, nces_schools):
  nces_school_titles = NCESSchool.get_nces_school_titles_from_nces_schools(nces_schools)
  most_relevant_nces_school_title = get_most_relevant_nces_school_title_with_wanted_school(wanted_school, nces_school_titles)[0]
  return NCESSchool.get_nces_school_from_nces_schools(most_relevant_nces_school_title, nces_schools)


def get_most_relevant_nces_school_title_with_wanted_school(wanted_school, nces_school_titles):
  return process.extractOne(wanted_school.title, nces_school_titles)


def main():
  OFFSET = 3886

  DUMP_NCES_FILE = './nces.dump'
  dump_nces_file = open(DUMP_NCES_FILE, 'a')

  NCES_SCHOOL_PUBLIC_DIR = './nces_schools_public'
  NCES_SCHOOL_PRIVATE_DIR = './nces_schools_private'

  ALL_NCES_SCHOOLS = {
    'public': load_all_nces_schools(NCES_SCHOOL_PUBLIC_DIR, False),
    'private': load_all_nces_schools(NCES_SCHOOL_PRIVATE_DIR, True)
  }

  WANTED_SCHOOL_FILE = 'schools.csv'  
  wanted_schools = WantedSchool.get_wanted_schools(WANTED_SCHOOL_FILE)

  offset_count = 1
  wanted_schools_count = 1
  wanted_schools_count_total = len(wanted_schools)
  for wanted_school in wanted_schools:
    if offset_count < OFFSET:
      offset_count = offset_count + 1
      wanted_schools_count = wanted_schools_count + 1
    
    else:
      print('[INFO] {0} / {1} Evaluating {2} - {3}'.format(wanted_schools_count, wanted_schools_count_total, wanted_school.title, wanted_school.state))
      
      nces_schools = ALL_NCES_SCHOOLS['private'] if wanted_school.is_private else ALL_NCES_SCHOOLS['public']
      if wanted_school.state != '' and wanted_school.state != '0':
        nces_schools = nces_schools[wanted_school.state]

        wanted_school, most_relevant_nces_school = fill_nces_of_wanted_school(wanted_school, nces_schools)
        dump_nces_file.write(most_relevant_nces_school.nces + '\n')
        print('[NCES] {0} Getting {1} - {2}'.format(most_relevant_nces_school.nces, most_relevant_nces_school.title, most_relevant_nces_school.state))
        print()
      else:
        dump_nces_file.write('NOT FOUND\n')
        print('[SKIP] {0}'.format(wanted_school.title))
        print()

      wanted_schools_count = wanted_schools_count + 1
    

if __name__ == '__main__':
  main()
