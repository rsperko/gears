#!/usr/bin/python

from optparse import OptionParser



parser = OptionParser()
parser.add_option("-w", "--wheel-inches", dest="wheelInches", default="27")
parser.add_option("-c", "--crankset", dest="crankSet")
parser.add_option("-o", "--cogset", dest="cogSet")
parser.add_option("-r", "--rpms", dest="rpms", default="90")

(options, args) = parser.parse_args()

if not options.crankSet or not options.cogSet:
	parser.print_help()
	exit()



class GearCombo:
	def __init__(self, cranksetGear, cogGear):
		self.cranksetGear = cranksetGear
		self.cogGear = cogGear
		self.related = []

	def calcGearRatio(self): 
		return (float(self.cranksetGear) / float(self.cogGear))

	def calcSpeed(self, wheelInches, rpms):
		gearDevInches = self.calcGearRatio() * wheelInches * 3.14
		gearDevFeet = gearDevInches / 12
		speed = gearDevFeet * rpms * 0.0114
		return speed

	def addRelated(self, gearCombo):
		self.related.append(gearCombo)

	def gearThumbprint(self):
		return int(self.calcGearRatio() * 10)

	def isUnique(self):
		return len(self.related) == 0

	def name(self):
		return str(self.cranksetGear) + 'x' + str(self.cogGear)

	def nameRelatives(self):
		output = ''
		for relative in self.related:
			if len(output) > 0:
				output = output + ', '
			output += relative.name()
		return output

	def numRelatives(self):
		return len(self.related)


class GearSet:
	def __init__(self, gearStrings):
		self.gears = []
		for gearString in gearStrings:
			self.gears.append(int(gearString.strip()))
		self._sortGears()

	def _sortGears(self):
		self.gears.sort()

	def inside(self, gear):
		return gear == self.gears[0]

	def outside(self, gear):
		return gear == self.gears[len(self.gears) - 1]

	def insideQuarter(self, gear):
		index = self.gears.index(gear);
		return index <= len(self.gears) / 4

	def outsideQuarter(self, gear):
		index = self.gears.index(gear);
		return index >= (len(self.gears) - len(self.gears) / 4) - 1


class Crankset(GearSet):
	def _sortGears(self):
		self.gears.sort()

class Cogset(GearSet):
	def _sortGears(self):
		self.gears.reverse()
	def output(self):
		print "Cogs"
		lastCogGear = None
		for cogGear in self.gears:
			print 'cog %(a)d: %(b)05.2f%%' % {'a': cogGear, 'b': self._percentChange(lastCogGear, cogGear)}
			lastCogGear = cogGear

	def _percentChange(self, lastCogGear, cogGear):
		if not lastCogGear or not cogGear:
			return 0
		percentageChange = 100.0 - ((float(lastCogGear) / cogGear) * 100)
		return percentageChange




class GearCombination:
	def __init__(self, crankSet, cogSet):
		self.crankSet = crankSet
		self.cogSet = cogSet
		self.combos = []
		for cranksetGear in crankSet.gears:
			for cogGear in cogSet.gears:
				self.combos.append(GearCombo(cranksetGear, cogGear))
		self._calculateRelationships()

	def _calculateRelationships(self):
		for gearComboA in self.combos:
			for gearComboB in self.combos:
				if gearComboA == gearComboB:
					continue
				if self.isRelated(gearComboA, gearComboB):
					gearComboA.addRelated(gearComboB)

	def isRelated(self, gearComboA, gearComboB):
		return gearComboA.gearThumbprint() == gearComboB.gearThumbprint()

	def isAccessible(self, gearCombo):
		if len(self.crankSet.gears) < 3:
			return True
		elif self.crankSet.inside(gearCombo.cranksetGear):
			return not self.cogSet.outside(gearCombo.cogGear)
		elif self.crankSet.outside(gearCombo.cranksetGear):
			return not self.cogSet.inside(gearCombo.cogGear)
		return True

	def isEasy(self, gearCombo):
		if len(self.crankSet.gears) < 3:
			return True
		elif self.crankSet.inside(gearCombo.cranksetGear):
			return not self.cogSet.outsideQuarter(gearCombo.cogGear)
		elif self.crankSet.outside(gearCombo.cranksetGear):
			return not self.cogSet.insideQuarter(gearCombo.cogGear)
		return True

	def output(self, wheelInches, rpms):
		unique = set()
		uniqueUsable = set()
		lastGearCombo = None
		minSpeed = 1000
		maxSpeed = 0
		usable = 0
		for gearCombo in self.combos:
			accessible = None
			if not self.isAccessible(gearCombo):
				accessible = 'X'
			elif not self.isEasy(gearCombo):
				# uniqueUsable.add(gearCombo.gearThumbprint())
				# usable = usable + 1
				accessible = '-'
			else:
				uniqueUsable.add(gearCombo.gearThumbprint())
				usable = usable + 1
				accessible = ' '
			minSpeed = min(minSpeed, gearCombo.calcSpeed(wheelInches, rpms))
			maxSpeed = max(maxSpeed, gearCombo.calcSpeed(wheelInches, rpms))
			unique.add(gearCombo.gearThumbprint())

			print "%(name)s %(ratio)05.2f %(speed)05.2fmph %(accessible)s %(relatives)s" % {'name': gearCombo.name(), 'ratio': gearCombo.calcGearRatio(), 'speed': gearCombo.calcSpeed(wheelInches, rpms), 'accessible': accessible, 'relatives': gearCombo.nameRelatives()}

			lastGearCombo = gearCombo

		gearGrade = float(len(uniqueUsable)) / len(self.combos) * 100

		print "\nSummary\n" \
			"gear: %(numGears)0d\n" \
			"unique gears: %(uniqueGears)0d\n" \
			"usable gears: %(usableGears)0d\n" \
			"unique usable gears: %(uniqueUsableGears)0d\n" \
			"percent unique usable gears: %(gearGrade)05.02f%%\n" \
			"max speed: %(maxSpeed)05.2f\n" \
			"min speed: %(minSpeed)05.2f\n" % {'numGears': len(self.combos), 'uniqueGears': len(unique), 'usableGears': usable, 'uniqueUsableGears': len(uniqueUsable), 'gearGrade': gearGrade, 'maxSpeed': maxSpeed, 'minSpeed': minSpeed}

		self.cogSet.output()


crankSet = Crankset(options.crankSet.split(','))
cogSet = Cogset(options.cogSet.split(','))

gearCombCollection = GearCombination(crankSet, cogSet)


gearCombCollection.output(float(options.wheelInches), int(options.rpms))


