#include <glibmm-2.4/glibmm/ustring.h>
#include <glibmm-2.4/glibmm/regex.h>
// #include <glib-2.0/glib/gregex.h>
#include <iostream>
#include <clocale>
#include <fstream>
#include <string>

using namespace std;
using namespace Glib;
// using namespace Glib;

int main()
{
    setlocale(LC_ALL, "en_US.utf8");
    string testString;  // Regular string buffer for std:: functions.    
    ifstream myfile("lyric1.html");
    
    int foundTitle=0;
    int foundUser =0;
    int foundEntry=0;
    // int scanning = 0;
    int terminated=0;
    
    // Found in the title bar
    RefPtr<Regex> titleRX = Regex::create("(?<=「).*(?=」)");
    
    RefPtr<Regex> userRX = Regex::create("(?<=\"/).*?(?=\" class=\"i_icon)");
    
    // Matches the line where the lyrics begin.
    RefPtr<Regex> entryRX = Regex::create("p id=\"_txt_main\"");
    
    // Match a single line of lyrics:
    RefPtr<Regex> firstLineRX = Regex::create("(?<=>).*(?=<br)");
    RefPtr<Regex> lyricRX = Regex::create("^.+(?=<br)");
    
    RefPtr<Regex> endRX = Regex::create("^.*(?=</p)");
    
    MatchInfo mInfo;
    
    while( getline(myfile, testString) )
    {
        if(!foundTitle)
        {
            if(titleRX->match(ustring(testString), mInfo))
            {
                foundTitle=1;
            }
        }
        else if(!foundUser)
        {
            if(userRX->match(ustring(testString), mInfo))
            {
                foundUser=1;
            }
        }
        else if(!foundEntry)
        {
            if(entryRX->match(ustring(testString), mInfo))
            {
                firstLineRX->match(ustring(testString), mInfo);
                foundEntry=1;
            }
        }
        else if(!terminated)
        {
            if(endRX->match(ustring(testString), mInfo))
                terminated=1;
            else
            {
                // scanning=1;
                lyricRX->match(ustring(testString), mInfo);
            }
        }
        else
            break;
        
        while(mInfo.matches())
        {
            for(int i=0; i<mInfo.get_match_count(); i++)
            {
                cout << mInfo.fetch(0) << endl;
            }
            
            mInfo.next();
        }
    }
    
    myfile.close();
    
    return 0;
}
