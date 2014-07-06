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
    
    RefPtr<Regex> regex = Regex::create("<a href=\"/t/.*?>"/*, G_REGEX_NEWLINE_LF, G_REGEX_MATCH_NEWLINE_LF*/);   // Destroy?
    MatchInfo miTest;   // Destroy
    
    int i, start, end;
    
    while( getline(myfile, testString) )
    {
        i=0;
        regex->match(ustring(testString), miTest);
        
        while(miTest.matches())
        {
            for(i=0; i<miTest.get_match_count(); i++)
            {
                cout << miTest.fetch(i) << endl;
            }
            
            miTest.next();
        }
    }
    
    myfile.close();
    
    return 0;
}
