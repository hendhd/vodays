#!/usr/bin/python
"""
This program spits out geojson for the VO Days GAVO has held.

This geojson can then be committed to github and viewed there.
"""

import json
import os
import re
import sys
import urllib

SRC_URL = "http://vo.ari.uni-heidelberg.de/arivo/On%20Tour?action=raw"
#SRC_URL = "http://localhost/ontour.txt"


class Waypoint(object):
	"""A geographical point point with a label.
	"""
	def __init__(self, lat, long, label):
		self.lat, self.long, self.label = lat, long, label
	
	def as_gpx(self):
		return "\n".join(['<wpt lat="%f" lon="%f">'%(self.lat, self.long),
			'<name>%s</name>'%self.label,
			'</wpt>'])
	
	def as_geojson(self):
		return {
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [self.long, self.lat],
				"url": "http://www.google.de"

      },
			"properties": {
				"name": self.label,
				"sym": None
			}
		}



class Points(object):
	"""A collection of waypoints.
	"""
	def __init__(self):
		self.waypoints = []
	
	def add_waypoint(self, waypoint):
		self.waypoints.append(waypoint)
	
	def as_gpx(self):
		return "\n".join([
			'<gpx version="1.0"'
			' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
			' xmlns="http://www.topografix.com/GPX/1/0">',
			]+[w.as_gpx() for w in self.waypoints]+[
			'</gpx>'])
	
	def as_geojson(self):
		return {
			"type": "FeatureCollection",
			"features": [
				p.as_geojson() for p in self.waypoints]}


def parse_on_tour(src_text):
	for mat in re.finditer(r"(?s)\{{3}(.*?)\}{3}", src_text):
		yield dict(l.split(":", 1) for l in mat.group(1).split("\n")
			if ":" in l)


def main():
	res = Points()
	for rec in parse_on_tour(urllib.urlopen(SRC_URL).read()):
		try:
			lat, long = map(float, rec["Geo"].split(","))
			res.add_waypoint(Waypoint(lat, long, rec["Institution"]))
		except KeyError:
			sys.stderr.write("Incomplete: %s\n"%rec["Institution"])
	with open("gavo_vo_days.geojson", "w") as f:
		json.dump(res.as_geojson(), f)


if __name__=="__main__":
	main()
