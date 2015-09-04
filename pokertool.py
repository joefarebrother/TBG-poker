#!/usr/bin/env python

#excuse my bad code, I haven't used python in ages

import os, sys, glob
old_dir = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) >= 2 and (sys.argv[1] == "-rep" or sys.argv[1] == "-reprm"):
	curr = sys.argv[2]
	overall = {}
	for line in open(curr + ".rep", "r"):
		print(line.strip())
		line = line.split()
		if line[1] == "paid":
			overall[line[0]] = overall.get(line[0], 0) - int(line[2])
		else:
			overall[line[0]] = overall.get(line[0], 0) + int(line[2])

	if sys.argv[1] == "-reprm":
		os.remove(curr + ".rep")

	print("Overall:")
	print("- The pot has " + open(curr + ".pot", "r").read())
	for key in overall.keys():
		if overall[key] < 0:
			print("- {0} is down {1}".format(key, -overall[key]))
		else:
			print("- {0} is up by {1}".format(key, overall[key]))

	os.chdir(old_dir)
	sys.exit(0)

def extract_digits(ts):
	return map(int, [d for d in ts if d in range(0, 10) or d in map(chr, range(ord("0"), ord("0") + 10))])

def parse_timestamp(ts):
	if ts == "01:23:45":
		return 1
	if ts == "12:34:56":
		return 2
	frequency = [0 for _ in range(10)]
	ts=extract_digits(ts)
	for digit in ts:
			frequency[digit] += 1
	if 6 in frequency:
		return 3
	if 5 in frequency:
		return 4
	if frequency.count(3) == 2:
		return 5
	if 4 in frequency:
		if 2 in frequency:
			return 6
		return 8
	if frequency.count(2) == 3:
		return 7
	if 3 in frequency:
		if 2 in frequency:
			return 9
		return 10
	if frequency.count(2) == 2:
		return 11
	if 2 in frequency:
		return 12
	return 13

def adjust_timezone(ts, tz):
	return str((int(ts[:2]) + tz) % 24).zfill(2) + ts[2:]

def is_second_better(ts1, ts2):
	ts1 = extract_digits(ts1)
	ts2	= extract_digits(ts2)
	if parse_timestamp(ts1) < parse_timestamp(ts2):
		return False
	if parse_timestamp(ts1) > parse_timestamp(ts2):
		return True
	if sum(ts1) > sum(ts2):
		return False
	if sum(ts1) < sum(ts2):
		return True
	return max(ts2) >= max(ts1)

def find_timezone(user):
	for tz_line in open("timezones", "r"):
		tz_line = tz_line.split()
		if tz_line[1].strip() == user.strip():
			return int(tz_line[0])
	tz = int(raw_input("Timezone? \n"))
	open("timezones", "a").write("{0} {1}\n".format(tz, user))
	return tz

def adjust_pot(curr, f):
	try:
		amt = int(open(curr + ".pot", "r").read())
	except Exception, e:
		amt = 0
	open(curr + ".pot", "w").write(str(f(amt)))

def collect_winnings(rank, pot, curr, user):
	if rank == 13:
		return pot
	won = int(pot/rank)
	if won > 0:
		open(curr + ".rep", "a").write("{0} won {1} (1/{2} of {3}) \n".format(user, won, rank, pot))
	return pot - won

try:

	while True:
		name = raw_input("Name? \n")
		tz = find_timezone(name)
		curr = raw_input("Currency? \n")
		amnt = int(raw_input("Amount? \n"))
		ts   = adjust_timezone(raw_input("GMT timestamp? \n"), tz)

		open(curr + ".rep", "a").write("{0} paid {1} \n".format(name, amnt))
		adjust_pot(curr, lambda x: x + amnt)

		run = open("run", "r").readlines()
		if len(run) == 0 or is_second_better(run[-1].split()[0], ts):
			open("run", "a").write("{0} {1} \n".format(ts, name))
		else: 
			for line in reversed(run):
				line = line.split()
				run_ts = line[0]
				run_name = line[1]
				print("Paying out? run_ts = {0}, run_name = {1}".format(run_ts, run_name)) #debug
				for curr in glob.glob("*.pot"):
					curr = curr[:-4]
					adjust_pot(curr, lambda pot: collect_winnings(parse_timestamp(run_ts), pot, curr, run_name))
			open("run", "w").write("{0} {1} \n".format(ts, name))

		if raw_input("Continue? (y/n) ") == "n":
			break


finally:
	os.chdir(old_dir)
