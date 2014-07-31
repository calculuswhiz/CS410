    #include <glibmm-2.4/glibmm/ustring.h>
#include <glibmm-2.4/glibmm/regex.h>
// #include <glib-2.0/glib/gregex.h>
#include <iostream>
#include <clocale>
#include <fstream>
#include <string>

/*#define HIRAGANA    ustring("[\u3041-\u3096]")
#define KATAKANA    ustring("[\u30A0-\u30FF]")
#define KANJI       ustring("[\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A]")
#define RADICALS    ustring("[\u2E80-\u2FD5]")
#define HALFKAT     ustring("[\uFF5F-\uFF9F]")
#define SYMBOL      ustring("[\u3000-\u303F]")
#define MISC        ustring("[\u31F0-\u31FF\u3220-\u3243\u3280-\u337F]")
#define ALPHANUM    ustring("[\uFF01-\uFF5E]")
#define ALLOFTHEM   HIRAGANA +"|"+ KATAKANA +"|"+ KANJI +"|"+ RADICALS +"|"+ HALFKAT +"|"+ SYMBOL +"|"+ MISC +"|"+ ALPHANUM*/

using namespace std;
using namespace Glib;

int main()
{
    setlocale(LC_ALL, "en_US.utf8");
    string testString;  // Regular string buffer for std:: functions.    
    ifstream myfile("page1.html");
    ustring trackString;
    
    RefPtr<Regex> regex = Regex::create("(?<=/t/).{4}");
    MatchInfo mInfo;
    int found=0;
    
    while( getline(myfile, testString) )
    {
        if( ustring(testString).find( "見つかりませんでした。")==ustring::npos )
            regex->match(ustring(testString), mInfo);
        else
            break;
        
        // cout << "what.\n";
        
        while(mInfo.matches())
        {
            for(int i=0; i<mInfo.get_match_count(); i++)
            {
                trackString = mInfo.fetch(i);
                if(!trackString.empty())
                {
                    found++;
                }
                
                if( found&1==1 )
                    cout << trackString << endl;
            }
            
            mInfo.next();
        }
    }
    
    myfile.close();
    
    return 0;
}
