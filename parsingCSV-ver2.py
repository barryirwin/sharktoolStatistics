#!/usr/lib/python

##PENDING:
###########gather the transmission period of each node

import csv
from decimal import Decimal
import sys, getopt #to manage arguments passed from CLI
import math

def main(argv):
	inputfile = ''
	outputfile = ''
	rows = 0 #augmenting the rows
	DoA = 0 #Difference of Arrival
	
	#Input file-related columns	
	epochColumn = 1
	sourceAddress = 2
	retryColumn = 3

	#Managing multi source stats
	registered = 0	#Just for having an output file where nodes are numbered for GNUPlot
	substraction = 0
	hostsNumbered = {}
	retransmissions = {}
	sxTransmissions = {}
	hostStatistics = {}
	firstArrivalPerHost = {}
	lastArrivalPerHost = {}
	source = ''

#------Managing the input file------#

	opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="]) #h and i are two of the options accepted (help and input)
								#semicolon next to i means that it accepts an argument (as well as with o)
	for opt,arg in opts:
		if opt == '-h':
			print 'parse.py -i <inputFile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	print 'Processing: ', inputfile
	print 'Outputting into: ', outputfile

#------Processing------#

	with open(inputfile, 'r') as file: #opens the file
		capture = list(csv.reader(file)) #stores the content of the csv as a list
		for lines in capture:
			#Numbering the nodes, not involved in computation#
			if capture[rows][sourceAddress] != "":
				source = capture[rows][sourceAddress]
				if rows == 0:	
					#DoA = 0
					hostsNumbered[source] = registered
				else:
					#DoA = Decimal(capture[rows][epochColumn]) - Decimal(capture[rows-1][epochColumn])
					if source not in hostsNumbered:
						registered += 1
						hostsNumbered[source] = registered
					
					
				"""#######################################################
				#Capturing successful transmission and retransmissions#
				#######################################################
				if capture[rows][retryColumn] != "Frame is not being retransmitted":
					countRetransmissions(source, retransmissions)
				else:
					countSxTransmissions(source, sxTransmissions)"""
					
				###################################################
				###########Capturing statistics per host###########
				#hostStatistics: {source:[0. DoA, 1. avgDoA, 2. stdDoA, 3. FirstTx, 4. LastTX, 5. ReTx, 6. SxTx]}
				###################################################
				if source in hostStatistics:
					hostStatistics[source][0].append(float(capture[rows][epochColumn]) - lastArrivalPerHost[source])
					if capture[rows][retryColumn] != "Frame is not being retransmitted":
						hostStatistics[source][5] += 1
					else:
						hostStatistics[source][6] += 1
				else:
					#Build a dictionary for the statistics
					hostStatistics[source] = [[],0,0,0,0,0,0]
					firstArrivalPerHost[source] = float(capture[rows][epochColumn])
					
				lastArrivalPerHost[source] = float(capture[rows][epochColumn])						
				
			rows += 1
	file.close()

	###########################################################
	#Completing the dictionary with the rest of the statistics#
	###########################################################
	for hosts in hostStatistics:
		###Average DoA###
		hostStatistics[hosts][1] = average(hostStatistics[hosts][0])
		###Standard deviation of DoA###
		hostStatistics[hosts][2] = std(hostStatistics[hosts][0])
		###First Transmission###
		hostStatistics[hosts][3] = firstArrivalPerHost[hosts]
		###Last Transmission###
		hostStatistics[hosts][4] = lastArrivalPerHost[hosts]
	
	
	##########################################
	#Printing to a plotable friendly format#
	##########################################	
	outputToFile(hostStatistics, hostsNumbered, outputfile)

	###############
	#Screen output#
	###############
	
	print "\n"
	print "###Retransmissions###"
	for key in hostStatistics:
		print "---Node ", key, " retransmissions: ", hostStatistics[key][5]
	print "\n"	
	
	print "###Successful Transmissions###"			
	for key in hostStatistics:
		print "+++Node:", key, " succcessful transmissions: ", hostStatistics[key][6]
		print "	  ---Average time between transmissions: ", hostStatistics[key][1], "s."
		print "		---Standard deviation: ", hostStatistics[key][2], "s."



#################
####Functions####
#################
def outputToFile(dict, hostNumbers, file):
	with open(file, 'w') as output:
		output.write("0. HostNumber, 1. IP, 2. avgDoA, 3. stdDoA, 4. FirstTx, 5. LastTX, 6. ReTx, 7. SxTx" + '\n')
		for key in dict:
			if key in hostNumbers:
				output.write(str(hostNumbers[key]) + ' ' + str(key) + ' ' + str(dict[key][1]) + ' ' + str(dict[key][2]) + ' ' + str(dict[key][3]) + ' ' + str(dict[key][4]) + ' ' + str(dict[key][5]) + ' ' + str(dict[key][6]) + '\n')
	output.close()


"""def outputFilePerNode(dict):
	listOfValues = []
	for key in dict:
		lines = 0
		nameOfFile = "Node-" + key
		listOfValues = dict[key]
		with open(nameOfFile, 'w') as output:
			for value in listOfValues:
				output.write(str(lines) + ' ' + str(value) + '\n')
				lines += 1
		output.close()"""
		

def average(listOfValues):	
	if len(listOfValues) > 0:
		numerator = 0
		counter = 0
		for item in listOfValues:
			numerator = numerator + item
			counter = counter + 1
		return numerator/counter
	else:
		return 0

def std(listOfValues):
	if len(listOfValues) > 1:
		numerator = 0
		counter = 0
		mean = average(listOfValues)
		for item in listOfValues:
			numerator = numerator + (math.fabs(item - mean)**(2))
			counter = counter + 1
		return (numerator/(counter - 1))**(0.5)
	else:
		return 0

"""def countRetransmissions(source, dictionary):
	if source not in dictionary:
		dictionary[source] =  1
	else:
		dictionary[source] +=  1
		
def countSxTransmissions(source, dictionary):
	if source not in dictionary:
		dictionary[source] = 1
	else:
		dictionary[source] += 1"""

if __name__ == "__main__":
	main(sys.argv[1:])