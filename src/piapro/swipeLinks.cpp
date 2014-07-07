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
    ifstream myfile("page1.html");
    
    RefPtr<Regex> regex = Regex::create("(?<=/t/).{4}(?=\")");
    MatchInfo miTest;
    
    while( getline(myfile, testString) )
    {
        regex->match(ustring(testString), miTest);
        
        while(miTest.matches())
        {
            for(int i=0; i<miTest.get_match_count(); i++)
            {
                cout << miTest.fetch(i) << endl;
            }
            
            miTest.next();
        }
    }
    
    myfile.close();
    
    return 0;
}
