#include <glibmm-2.4/glibmm/ustring.h>  // UTF8 string
#include <glibmm-2.4/glibmm/regex.h>    // UTF8 regex
#include <iostream> // Streams
#include <cstdio>   // popen
#include <clocale>  // Set to UTF-8
#include <fstream>  // fileio
#include <string>   // std::string for line-by-line.
#include <cstdlib>  // System, randoms
#include <thread>   // sleep function
#include <ctime>    // Random
#include <sstream>  // concatenation
#include <chrono>

#define STARTPAGE 1

using namespace std;
using namespace Glib;

int links2File(string str);

void writeEntry(string str);
void writeIndex(string str);

int main()
{
    // UTF-8 string stuff:
    setlocale(LC_ALL, "en_US.utf8");
    
    system ("mkdir index");
    system ("rm linkFile.txt");
    
    ustring baseCom = "curl 'http://piapro.jp/text/?categoryId=7&page=";
    ustring endCom = "' > 'temp.html'";
    stringstream sstr;
    ustring newCom;
    
    // Sleep stuff.
    srand(time(NULL));  // Init random for curl commands.
    
    // popen file pointer:
    FILE * fp;
    
    int pageNo=STARTPAGE;   // page counter.  append to URL.
    
    // Send URL request until break.
    while(1)
    {
        // Make URL.
        sstr << baseCom << pageNo << endCom;
        newCom = sstr.str();
        
        cout << pageNo << ":" << newCom << endl;
        // cout << newCom << endl;
        
        sstr.str("");
        
        if( links2File(newCom)==-1 )
        {
            cout << "Done. Page# = " << pageNo << endl;
            break;
        }
        else
            pageNo++;
        
        this_thread::sleep_for (chrono::seconds(rand()%2+1));
    }
    
    system("rm temp.html");
    
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
    
    writeIndex(string(line));
    
    return 0;
}

int links2File(string str)
{
    RefPtr<Regex> regex = Regex::create("(?<=/t/).{4}");
    MatchInfo mInfo;
    
    // string sConvert = ss.str();
    
    // Initiate curl.
    system(str.c_str()); // curl [URL] > temp.html
    
    string tempString;  // std::string for conversion.
    ustring trackString; // ignore duplicates.
    ifstream myFile("temp.html");
    ofstream exFile("linkFile.txt", ofstream::out | ofstream::app);
    
    int found = 0;
    
    while( getline(myFile, tempString) )
    {
        if( ustring(tempString).find( "見つかりませんでした。")==ustring::npos )
            regex->match(ustring(tempString), mInfo);
        else
            return -1;
        
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
                    exFile << trackString << endl;
            }
            
            mInfo.next();
        }
    }
    
    myFile.close();
    exFile.close();
    return 0;
}

void writeIndex(string str)
{
    ustring baseCom = "curl 'http://piapro.jp/t/";
    ustring endCom = "' > 'temp.html'";
    stringstream sstr;
    // ustring title;
    // ustring newCom;
    
    string tempString;
    
    ifstream inFile("linkFile.txt");
    
    int counter = 1;
    
    while( getline(inFile, tempString) )
    {
        cout << "Link #: " << counter << " of " << str <<endl;
        counter++;
        sstr << baseCom << tempString << endCom;
        // newCom = sstr.str();
        system( sstr.str().c_str() );
        
        sstr.str("");
        
        // Create entry with title.
        writeEntry(tempString);
        this_thread::sleep_for (chrono::seconds(rand()%2+1));
    }
    
    inFile.close();
}

void writeEntry(string str)
{
    ifstream outFile("temp.html");
    ofstream entryFile("./index/"+str);
    string tempString;
    
    entryFile << "http://piapro.jp/t/" << str << endl;
    
    // string title;
    
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
    
    while( getline(outFile, tempString) )
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
                entryFile << "J\n";
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
                entryFile << mInfo.fetch(i) << endl;
            }
            
            mInfo.next();
        }
    }
    
    outFile.close();
    entryFile.close();
}
