#include <glibmm-2.4/glibmm/ustring.h>  // UTF8 string
#include <glibmm-2.4/glibmm/regex.h>    // UTF8 regex
#include <iostream> // Streams
#include <cstdio>   // popen
#include <clocale>  // Set to UTF-8
#include <fstream>  // fileio
#include <string>   // std::string for line-by-line.
#include <cstdlib>  // System, randoms
#include <sstream>  // concatenation

using namespace std;
using namespace Glib;

// int links2File(string str);

void writeFile(string str);
void processHTM(string str);

int main()
{
    // UTF-8 string stuff:
    setlocale(LC_ALL, "en_US.utf8");
    
    system ("mkdir index");
    system ("mkdir outdex");
    // system ("rm linkFile.txt");
    
    // popen file pointer:
    FILE * fp;
    
    if( (fp=popen("wc -l < linkFile.txt", "r")) == NULL )
    {
        cout << "Error.\n";
        return -1;
    }
    
    char * line = NULL;
    size_t len = 0;
    // ssize_t read;
    
    getline(&line, &len, fp);
    printf("lines: %s\n", line);
    
    pclose(fp);
    
    processHTM(string(line));
    
    return 0;
}

void processHTM(string str)
{
    // stringstream sstr;
    // ustring title;
    // ustring newCom;
    
    string tempString;
    
    ifstream inFile("linkFile.txt");
    
    int counter = 1;
    
    while( getline(inFile, tempString) )
    {
        cout << "Link #: " << counter << " of " << str <<endl;
        counter++;
        // newCom = sstr.str();
        // system( sstr.str().c_str() );
        
        // sstr.str("");
        
        // Create entry with title.
        writeFile(tempString);
    }
    
    inFile.close();
}

void writeFile(string str)
{
    ifstream inFile("./index/"+str);
    ofstream outFile("./outdex/"+str);
    string tempString;
    
    outFile << "http://piapro.jp/t/" << str << endl;

    // int foundTitle=0;        state: 0
    // int foundUser =0;        state: 1
    // int foundEntry=0;        state: 2
    // int terminated=0;        state: 3
    
    int state = 0;
    
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
    
    while( getline(inFile, tempString) )
    {
        if(state == 0)  // Title
        {
            if(titleRX->match(ustring(tempString), mInfo))
            {
                state=1;
            }
        }
        else if(state == 1) // Author
        {
            if(userRX->match(ustring(tempString), mInfo))
            {
                state = 2;
            }
        }
        else if(state == 2) // Lyrics start
        {
            if(entryRX->match(ustring(tempString), mInfo))
            {
                outFile << "J\n";
                firstLineRX->match(ustring(tempString), mInfo);
                state = 3;
            }
        }
        else if(state == 3)
        {
            if(endRX->match(ustring(tempString), mInfo))
                state = 4;
            else
            {
                lyricRX->match(ustring(tempString), mInfo);
            }
        }
        else
            break;
        
        while(mInfo.matches())
        {
            for(int i=0; i<mInfo.get_match_count(); i++)
            {
                outFile << mInfo.fetch(i) << endl;
            }
            
            mInfo.next();
        }
    }
    
    inFile.close();
    outFile.close();
}
