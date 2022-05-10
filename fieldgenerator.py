from matplotlib.style import use
import pygame
from pygame.constants import *
from math import sin,cos,pi, atan
from numpy import array
import numpy as np

k = 9 * 10**9 #Nm^2/s^2

pygame.init()
clock = pygame.time.Clock()

width, height = 1000, 900

screen = pygame.display.set_mode((width, height), 0, 32)
screen.fill((255,255,255))
pygame.display.set_caption("Electric Field")
sign_font = pygame.font.SysFont('arial', 30, bold=True)
charge_font = pygame.font.SysFont('arial', 17, bold=True)

particles = []
arrows = []

class Particle():
  def __init__(self, positionx, positiony, charge=1):
    self.sign = "+" if charge>0 else "-" if charge < 0 else "0"

    self.charge = charge * 1.6 * 10**(-19)

    self.position = (positionx,positiony)
    self.color = (255,0,0) if self.sign=="+" else (255,255,0) if self.sign=="-" else (0,255,255)
    self.rect = pygame.draw.circle(screen, self.color, self.position, 25)

  def draw(self):
    self.rect = pygame.draw.circle(screen, self.color, self.position, 25)
    sign_loc = (self.rect.centerx-7,self.rect.centery-25) if self.sign=="+" or self.sign=="0" else (self.rect.centerx-3,self.rect.centery-30)
    screen.blit(sign_font.render(self.sign, False, (0,0,0)),sign_loc)

    charge = round(self.charge/(1.6 * 10**(-19)), 2)
    if charge > 0:
      charge = "+" + str(charge) + "e"
    else:
      charge = str(charge) + "e"
    charge_loc = (self.position[0]- 12 - len(str(charge)),self.position[1]-2)
    screen.blit(charge_font.render(charge, False, (0,0,0)), charge_loc)

  def draw_preview(self, user_text):
    self.rect = pygame.draw.circle(screen, self.color, self.position, 25)
    sign_loc = (self.rect.centerx-7,self.rect.centery-25) if self.sign=="+" or self.sign=="0" else (self.rect.centerx-3,self.rect.centery-30)
    screen.blit(sign_font.render(self.sign, False, (0,0,0)),sign_loc)

    charge_loc = (self.position[0]- 12 - len(user_text),self.position[1]-2)
    screen.blit(charge_font.render(user_text, False, (0,0,0)), charge_loc)

class Arrow():
  def __init__(self, positionx, positiony, angle, color = (0,0,0)):
    self.position = [positionx,positiony]
    self.angle = angle
    self.color = color
  
  def draw(self):
    angle = self.angle
    r = 20
    B = self.position
    E = [B[0] + r*cos(angle), B[1] - r*sin(angle)]
    I = [B[0] + 0.75*r*cos(angle), B[1] - 0.75*r*sin(angle)]
    L = [I[0] - 0.1*r*sin(angle), I[1] - 0.1*r*cos(angle)]
    R = [I[0] + 0.1*r*sin(angle), I[1] + 0.1*r*cos(angle)]
    #print(I, L, R)
    points = [B,I,L,E,R,I]
    for point in points:
      point[0] = int(point[0])
      point[1] = int(point[1])
        
    pygame.draw.polygon(screen, self.color, points,3)

def true_angle(h,w):
  direction = None
  if h  > 0:
    if w > 0:
      quad = 1
    elif w < 0:
      quad = 2
    else:
      direction = pi/2

  elif h < 0:
    if w > 0:
      quad = 4
    elif w < 0:
      quad = 3
    else:
      direction = -pi/2
  else:
    if w > 0:
      direction = 0
    else:
      direction = pi

  if direction == None:
    direction = atan(h/w)
    if direction > 0 and quad == 1:
      direction = direction
    elif direction > 0 and quad == 3:
      direction = pi + direction
    elif direction < 0 and quad == 4:
      direction = direction
    elif direction < 0 and quad ==2:
      direction = pi + direction
  
  return direction



def create_field(particles):
  column_width = width/50
  row_width = height/50
  arrows = []

  for col in range(50):
    col_coord = col * column_width

    for row in range(50):
      row_coord = row * row_width
    
      vectors = []
      for particle in particles:
        if abs(col_coord - particle.position[0]) < 50 and abs(row_coord - particle.position[1]) < 50:
          vectors = []
          break

        h = particle.position[1] - row_coord
        w = col_coord - particle.position[0]

        d = ((w)**2 + (h)**2)*(1/2) * 10**-10 #angstroms

        E = k*particle.charge/(d**2)

        direction = true_angle(h,w)

        Evec =  array([E*cos(direction), E*sin(direction)])
        vectors.append(Evec)

      if len(vectors) != 0:
        Etotal = sum(vectors)
        angle = true_angle(Etotal[1], Etotal[0])
        arrows.append(Arrow(col_coord,row_coord,angle))

  return arrows

particles.append(Particle(500,450))
particles.append(Particle(500,100, -1))
particles.append(Particle(500,700, -10))
#particles.append(Particle(500,100, -1))

#arrows.append(Arrow(500,300, pi/6))

change_charge = None
user_text = ""
while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      quit()

    if event.type == MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pygame.mouse.get_pos()
      for idx, particle in enumerate(particles):
        if change_charge != None:
          break
        if particle.rect.collidepoint(mouse_pos) == True:
          change_charge = idx
          particle.color = (144,238,144)
          particle.charge = 0
          particle.sign = "0"
          break

      else:
        particles.append(Particle(mouse_pos[0], mouse_pos[1], 1))
    
    if event.type == MOUSEBUTTONDOWN and event.button == 2:
      particles = []
    
    if event.type == MOUSEBUTTONDOWN and event.button == 3:
      if change_charge == None:
        mouse_pos = pygame.mouse.get_pos()
        particles.append(Particle(mouse_pos[0], mouse_pos[1], -1))
    
    if event.type == pygame.KEYDOWN:
      if change_charge != None:
        p = particles[change_charge]

        if event.key == pygame.K_BACKSPACE:
          user_text = user_text[:-1]

        if event.key == pygame.K_RETURN:
          try:
            p.charge = float(user_text)* 1.6 * 10**(-19)
          except ValueError:
            p.charge = 0

          p.sign = "+" if p.charge>0 else "-" if p.charge < 0 else "0"
          p.color = (255,0,0) if p.sign=="+" else (255,255,0) if p.sign=="-" else (0,255,255)

          change_charge = None
          user_text = ""

        else:
          user_text += event.unicode


  screen.fill((255,255,255))
  for idx, particle in enumerate(particles):
    if idx != change_charge:
      if float(particle.charge/(1.6*10**-19)) == 0:
        del particles[idx]
      else:
        particle.draw()
    if idx == change_charge:
      particle.draw_preview(user_text)

  arrows = create_field(particles)

  for arrow in arrows:
    arrow.draw()

  pygame.display.flip()
  clock.tick(120)