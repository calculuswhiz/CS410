all:
	make swipeLinks swipeLyrics
	
swipeLinks:
	g++ -g -std=c++0x swipeLinks.cpp -o swipeLinks `pkg-config libxml++-2.6 --cflags glib-2.0 --libs glib-2.0`

swipeLyrics:
	g++ -g -std=c++0x swipeLyrics.cpp -o swipeLyrics `pkg-config libxml++-2.6 --cflags glib-2.0 --libs glib-2.0`
	
clean:
	rm swipeLinks swipeLyrics
