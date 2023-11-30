import datetime
import os
import random
import requests
import string
import time

SERVER_BASE = 'https://GalConServer.sirgnip.repl.co'


class ApiException(Exception):
  pass


def log(msg):
  print(str(datetime.datetime.now()) + ' ' + str(msg))


def clear():
  print("\033c", end="")
  # replit.clear()


def make_map(width, height):
  s = ''
  s += '=' * width
  s += '\n'
  for row in range(height - 2):
    if random.randint(1, 3) == 1:
      s += str(row) + random.choice(string.ascii_letters) * random.randint(
          1, 5) + '\n'
    else:
      s += '|' + (' ' * (width - 2)) + '|'
      s += '\n'
  s += '=' * width
  return s


def spinner(iter_count):
  txt = '|/-\\'
  for iter in range(iter_count):
    for char in txt:
      clear()
      print(' ' * 20 + char)
      time.sleep(0.1)


# do a call, return data
# if an error, throw an exception
# Input: url, params


def api_call(url, params=None):
  resp = requests.get(url, params=params)
  # resp = requests.get(urk, params=params, timeout=60)
  if resp.ok:
    return resp.json()
  else:
    #raise ApiException(f'Error: {resp.status_code} {resp.json()}')
    raise ApiException(
        f'ERROR:#{resp.status_code} URL:{resp.url}\n{resp.text}')


def api_debug():
  log('start')
  slug = os.getenv('REPL_SLUG')
  delay = 3
  url = f'{SERVER_BASE}/debug_blocking/client_{slug}/{delay}'
  api_query(url)
  log('done')


def _show_map(planets):
  WIDTH, HEIGHT = 20, 20
  BORDER = '#'

  # place planets in grid
  grid = [['.' for x in range(WIDTH)] for y in range(HEIGHT)]
  for p in planets:
    x, y = p['x'], p['y']
    grid[y][x] = p['name'][0]
  grid.insert(0, BORDER * WIDTH)
  grid.append(BORDER * WIDTH)

  # convert grid to printable string
  out = ''
  for row in grid:
    out += BORDER + (''.join(row)) + BORDER + '\n'
  return out


def _show_game(me, game):
  print('--- STATE:', game['state'], f'({me})')
  print('--- Clients: -----------')
  print('\n'.join(['- ' + c for c in game['clients']]))
  print('--- Planets: -----------')
  print(_show_map(game['planets']))
  print('\n'.join(['- ' + f'{p["name"]} {p["owner"]} {p["ships"]} +{p["production"]} {p["x"]},{p["y"]}' for p in game['planets']]))
  print('--- Turns: -----------')
  print('\n'.join(['- ' + t for t in game['fleets']]))
  

def client(name):
  log(f'name {name}')
  url_login = f'{SERVER_BASE}/login/{name}'
  url_start = f'{SERVER_BASE}/start'
  url_turn = f'{SERVER_BASE}/turn'
  resp = api_call(url_login)
  _show_game(name, resp)
  while True:
    print()
    r = input('[R]efresh or [S]tart: ')
    clear()
    if r.upper() == 'R':
      resp = api_call(url_login)
      if resp['state'] == 'LOBBY':
        _show_game(name, resp)
      elif resp['state'] == 'PLAYING':
        print('Someone started game...')
        _show_game(name, resp)
        break
    elif r.upper() == 'S':
      resp = api_call(url_start)
      print('I started game with:')
      _show_game(name, resp)
      print('I started the game...')
      break

  while True:
    print()
    r = input('Enter turn: ')
    clear()
    resp = api_call(url_turn, params={'player': name, 'turn': r})
    _show_game(name, resp)
    if resp['state'] == 'END':
      break
  
  print(f'Game is complete with {len(resp["fleets"])} turns')
  print('DONE')


def status():
  log('status')
  url = '{SERVER_BASE}/status'
  txt = api_call(url)
  print('-' * 40, 'Clients...')
  print(txt)
  print('-' * 40)


def main():
  # spinner(20)
  #api_debug()

  name = input('Enter name: ')
  # name = 'gnip'
  client(name)


if __name__ == "__main__":
  main()
"""Issues
- what if I try to start game after someone else already has?"""
