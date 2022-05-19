from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
from neo4j import GraphDatabase
import requests

# Create your views here.

import nltk
from nltk import tokenize
from operator import itemgetter
import math
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
nltk.download('stopwords')
nltk.download('punkt')
stop_words = list(set(stopwords.words('english')))
import cdata.salesforce as mod3
import cdata.jira as mod4

taggs=dict()
finaltags=[]
uniqueId=""

def home(request):
    return HttpResponse("hello, your response has been sent");

def contribute(request):
    if request.method == "POST":
        ptype=request.POST['ptype']
        itype=request.POST['itype']
        psummary=request.POST['psummary']
        pdescription=request.POST['pdescription']
        products=request.POST.getlist('products')
        kanalysis=request.POST['kanalysis']
        kinsights=request.POST['kinsights']
        owner=request.POST['owner']
        conn = MongoClient()
        db=conn.knowledgeplatform
        collection=db.knowledge

        #making a collection to send to mongo database
        rec1={
        #   "username":username1,          
          "ptype":ptype,
          "psummary":psummary,
          "pdescription":pdescription,
          "products":products,
          "kanalysis":kanalysis,
          "kinsights":kinsights,
          "owner":owner,
          "ID":owner+str(len(psummary))+str(len(pdescription))+str(len(kinsights)+len(kanalysis)),
          "tags":finaltags,

        }
        global uniqueId
        uniqueId=owner+str(len(psummary))+str(len(pdescription))+str(len(kinsights)+len(kanalysis))
        print("uniqueId inside contribute",uniqueId)
        generateTags(psummary,pdescription)
        
        collection.insert_one(rec1)
       
        tags_string=""
        for i in finaltags:
            tags_string+=i+","
        print(finaltags,"finallllllllllllllllllll",tags_string)
        tags_string=tags_string[:-1]
        # conn=MongoClient()
        # db=conn.knowledgeplatform
        # collection=db.knowledge
        # db.knowledge.update({'ID':uniqueId},{"$set":{'tags':finaltags}})
        products_string=""
        for i in products:
            products_string+=i+","
        products_string=products_string[:-1]

        graphdb=GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "admin"))
        session=graphdb.session()
        q2='''Merge (kp:knowledge {pdescription: '%s', ptype: '%s', psummary: '%s' , kanalysis:'%s', kinsights:'%s', products:'%s', tags: '%s', owner:'%s'})
        WITH kp
        UNWIND split('%s',',') AS tag
        MERGE (t:tags_string {tagname:tag})
        MERGE (kp)-[:belongs_to]->(t)
        '''%(pdescription,ptype,psummary,kanalysis,kinsights,products_string,tags_string,owner, tags_string)

        # q2='''Merge (kp:knowledge {pdescription: '%s', ptype: '%s', psummary: '%s', kanalysis:'%s', kinsights:'%s', products:'%s',tags:'%s'})
        # WITH kp
        # UNWIND split('%s',',') AS tag
        # MERGE (t:final_Tags {tagname: tag})
        # MERGE (kp)-[:belongs_to]->(t)'''%(pdescription,ptype,psummary,kanalysis,kinsisghts,products_string,final_Tags[:-1],datetime_entry.strftime('%Y-%m-%d %H:%M:%S'),final_Tags[:-1])

        q1=" match(n) return n "

        session.run(q2)
        session.run(q1)

        conn=MongoClient()
        db=conn.knowledgeplatform
        collection=db.knowledge
        ourdata=collection.find({'ID':uniqueId})
        ddd={'t':finaltags,'ourdata':ourdata.clone()}
        #return render(request,'tagsgeneration.html',ddd)
        return render(request,'contribute.html',ddd)

        #return redirect("home")
      
    return render(request,"contribute.html")

def tagsgeneration(request):
    if request.method == "POST":
        ymtags=request.POST.getlist('ymtags')
        additionalTags=request.POST['additionalTags']
        additionalTags=additionalTags.split(",")
        total_list_tags=ymtags+additionalTags
        print("generated tags ",ymtags)
        print("additional tags ",additionalTags)
        print("final list of tags ",total_list_tags)
        conn=MongoClient()
        db=conn.knowledgeplatform
        collection=db.knowledge
        db.knowledge.update({'ID':uniqueId},{"$set": {'tags':total_list_tags}})

    # return render(request,'contribute.html')
    return redirect("home")
    # return render(request,'tagsgeneration.html')


def generateTags(a,b):   
    #stopwords for removing less important words from document
    more_stop_words = ["weren't", 'needn', "mustn't",'8;', '2)on', "needn't", 'haven', "wouldn't", 'most', 'only', 'down', 'over', 'mightn', 'where', 'this', 'your', "shouldn't", "you'll", 'so', 'weren', 'will', 'hadn', 'hasn', 'i', 'no', 'which', 'has', 'those', 'itself', 'they', 'whom', 'that', 'isn', 'couldn', 'as', 'doesn', "haven't", 'other', 'too', 'inserting', 'running', 'showing', 'picking', '3)query', 'calllogs', '(outcome', 'starttime', 'endtime', 'than', 'is', 'his', "don't", 'mustn', 'she', 'just', "hadn't", 'through', 'been', 'an', 'with', 'more', 'from', 'few', 'how', 'own', 't', 'were','template', 'being', 'above', 'both', 'it', "hasn't", 'these', 'wouldn', 'during', 'our', 'didn', 'all', 'should', "didn't", 'further', 'or', 'have', 'in', 'her', 'here', 'yourselves', 'did', 'a', 'its', 'of', 'about', "couldn't", "should've", 'after', 'some', 'the', 'at', 'be', 'aren', 'each', 'shan', 'won', 'he', 'my', 'why', 've', 'same', "doesn't", 's', 'up', 'now', 'ain', 'we', "shan't", 'what', 'below', 'then', 'such', "mightn't", 'me', 'out', 'do', "she's", 'm', "it's", "that'll", "isn't", 'y', 'yours', 'against', 'into', 'herself', 'under', 'who', 'wasn', 'by', "aren't", 'any', 'are', 'does', 'but', 'because', 'and', 'doing', 'until', 'off', 'very', "you'd", 'ourselves', 'was', 'once', 're', 'between', 'him', 'd', 'myself', 'can', 'ma', 'if', 'for', 'yourself', 'o', 'them', 'am', "you've", 'nor', 'don', 'you', 'when', 'had', 'on', 'not', "wasn't", "won't", 'ours', 'before', 'while', 'himself', 'themselves', 'shouldn', "you're", 'to', 'having', 'their', 'again', 'theirs', 'there', 'hers', 'll', ' able', 'about', 'above', 'abroad', 'according', 'accordingly', 'across', 'actually', 'adj', 'after', 'afterwards', 'again', 'against', 'ago', 'ahead', "ain't", 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'alongside', 'already', 'also', 'although', 'always', 'am', 'amid', 'amidst', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', "aren't", 'around', 'as', "a's", 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'back', 'backward', 'backwards', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'begin', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 'came', 'can', 'cannot', 'cant', "can't", 'caption', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', "c'mon", 'co', 'co.', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', "couldn't", 'course', "c's", 'currently', 'dare', "daren't", 'definitely', 'described', 'despite', 'did', "didn't", 'different', 'directly', 'do', 'does', "doesn't", 'doing', 'done', "don't", 'down', 'downwards', 'during', 'each', 'edu', 'eg', 'eight', 'eighty', 'either', 'else', 'elsewhere', 'end', 'ending', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'evermore', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'fairly', 'far', 'farther', 'few', 'fewer', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'forever', 'former', 'formerly', 'forth', 'forward', 'found', 'four', 'from', 'further', 'furthermore', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', "hadn't", 'half', 'happens', 'hardly', 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', "here's", 'hereupon', 'hers', 'herself', "he's", 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'hundred', "i'd", 'ie', 'if', 'ignored', "i'll", "i'm", 'immediate', 'in', 'inasmuch', 'inc', 'inc.', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'inside', 'insofar', 'instead', 'into', 'inward', 'is', "isn't", 'it', "it'd", "it'll", 'its', "it's", 'itself', "i've", 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'known', 'knows', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', "let's", 'like', 'liked', 'likely', 'likewise', 'little', 'look', 'looking', 'looks', 'low', 'lower', 'ltd', 'made', 'mainly', 'make', 'makes', 'many', 'may', 'maybe', "mayn't", 'me', 'mean', 'meantime', 'meanwhile', 'merely', 'might', "mightn't", 'mine', 'minus', 'miss', 'more', 'moreover', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', "mustn't", 'my', 'myself', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', "needn't", 'needs', 'neither', 'never', 'neverf', 'neverless', 'nevertheless', 'new', 'next', 'nine', 'ninety', 'no', 'nobody', 'non', 'none', 'nonetheless', 'noone', 'no-one', 'nor', 'normally', 'not', 'nothing', 'notwithstanding', 'novel', 'now', 'nowhere', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', "one's", 'only', 'onto', 'opposite', 'or', 'other', 'others', 'otherwise', 'ought', "oughtn't", 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'particular', 'particularly', 'past', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provided', 'provides', 'que', 'quite', 'qv', 'rather', 'rd', 're', 'really', 'reasonably', 'recent', 'recently', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 'round', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'since', 'six', 'so', 'some', 'somebody', 'someday', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 'take', 'taken', 'taking', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', "that'll", 'thats', "that's", "that've", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', "there'd", 'therefore', 'therein', "there'll", "there're", 'theres', "there's", 'thereupon', "there've", 'these', 'they', "they'd", "they'll", "they're", "they've", 'thing', 'things', 'think', 'third', 'thirty', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'till', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', "t's", 'twice', 'two', 'un', 'under', 'underneath', 'undoing', 'unfortunately', 'unless', 'unlike', 'unlikely', 'until', 'unto', 'up', 'upon', 'upwards', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'v', 'value', 'various', 'versus', 'very', 'via', 'viz', 'vs', 'want', 'wants', 'was', "wasn't", 'way', 'we', "we'd", 'welcome', 'well', "we'll", 'went', 'were', "we're", "weren't", "we've", 'what', 'whatever', "what'll", "what's", "what've", 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', "where's", 'whereupon', 'wherever', 'whether', 'which', 'whichever', 'while', 'whilst', 'whither', 'who', "who'd", 'whoever', 'whole', "who'll", 'whom', 'whomever', "who's", 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'wonder', "won't", 'would', "wouldn't", 'yes', 'yet', 'you', "you'd", "you'll", 'your', "you're", 'yours', 'yourself', 'yourselves', "you've", 'zero', 'a', "how's", 'i', "when's", "why's", 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'uucp', 'w', 'x', 'y', 'z', 'I', 'www', 'amount', 'bill', 'bottom', 'call', 'computer', 'con', 'couldnt', 'cry', 'de', 'describe', 'detail', 'due', 'eleven', 'empty', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'forty', 'front', 'full', 'give', 'hasnt', 'herse', 'himse', 'interest', 'itse”', 'mill', 'move', 'myse”', 'part', 'put', 'show', 'side', 'sincere', 'sixty', 'system', 'ten', 'thick', 'thin', 'top', 'twelve', 'twenty', 'abst', 'accordance', 'act', 'added', 'adopted', 'affected', 'affecting', 'affects', 'ah', 'announce', 'anymore', 'apparently', 'approximately', 'aren', 'arent', 'arise', 'auth', 'beginning', 'beginnings', 'begins', 'biol', 'briefly', 'ca', 'date', 'ed', 'effect', 'et-al', 'ff', 'fix', 'gave', 'giving', 'heres', 'hes', 'hid', 'home', 'id', 'im', 'immediately', 'importance', 'important', 'index', 'information', 'invention', 'itd', 'keys', 'kg', 'km', 'largely', 'lets', 'line', "'ll", 'means', 'mg', 'million', 'ml', 'mug', 'na', 'nay', 'necessarily', 'nos', 'noted', 'obtain', 'obtained', 'omitted', 'ord', 'owing', 'page', 'pages', 'poorly', 'possibly', 'potentially', 'pp', 'predominantly', 'present', 'previously', 'primarily', 'promptly', 'proud', 'quickly', 'ran', 'readily', 'ref', 'refs', 'related', 'research', 'resulted', 'resulting', 'results', 'run', 'sec', 'section', 'shed', 'shes', 'showed', 'shown', 'showns', 'shows', 'significant', 'significantly', 'similar', 'similarly', 'slightly', 'somethan', 'specifically', 'state', 'states', 'stop', 'strongly', 'substantially', 'successfully', 'sufficiently', 'suggest', 'thered', 'thereof', 'therere', 'thereto', 'theyd', 'theyre', 'thou', 'thoughh', 'thousand', 'throug', 'til', 'tip', 'ts', 'ups', 'usefully', 'usefulness', "'ve", 'vol', 'vols', 'wed', 'whats', 'wheres', 'whim', 'whod', 'whos', 'widely', 'words', 'world', 'youd', 'youre', 'size', 'problem', 'set', 'include', 'custom', 'false', 'able', 'facing', 'issue', 'connecting', 'working', '', '#', '!', '@', '$', '%', '^', '·', '&', '', '(', ')', '_', '-', '+', '=', '~', '`', ',', '.', '?', '/', ':', ';', 'execute', 'customer', 'wants', 'improve', 'information', 'like', 'create', 'high', 'contains', 'data', 'server', 'when', 'hi', 'hey', 'hello', 'error', 'good', 'user', 'add', 'attempt', 'we', 'lot', 'its', 'use', 'such', 'make', 'record', 'return', 'message', 'example', 'name', 'you', 'handling', 'found', 'that', 'received', 'getting', 'setting', 'large', 'small', 'tiny', 'huge', 'big', 'contain', 'made', 'new', 'address', 'attempt', 'please', 'hi,', 'hello,', 'hey,', 'so,', 'so', 'since', 'suggest', 'has', 'have', 'had', 'this', 'do', 'done', 'go', 'to', 'went', 'though', 'saved', 'although', 'generally', 'literally', 'enter', 'enters', 'center', 'same', 'if', 'else', 'for', 'while', '', '',"#", "!", "@", "$", "%", "^",'·', "&", "", "(", ")", "_", "-", "+", "=", "~", "`",",", ".", "?","/", ":", ";", "execute", "customer", "wants", "improve",   "information","like","create", "high", "contains", "data", "server", "when", "hi", "hey", "hello", "error", "good" , "user", "add", "attempt", "we", "lot" , "its", "use", "such", "make", "record", "return", "message", "example", "name", "you", "handling", "found", "that", "received", "getting", "setting", "large", "small", "tiny", "huge", "big","contain", "made", "new", "address", "attempt","please","hi," ,"hello,","hey,","so,","so", "since", "suggest", "has", "have", "had", "this", "do", "done", "go", "to", "went", "though","saved", "although", "generally", "literally", "enter", "enters", "center", "same", "if", "else", "for", "while","heavy","asked", "share", "path",'maintain', 'multiple', 'place', 'templatefile','2020', '2021', 'longer', 'recognized', 'valid','code', 'returned', 'inquiry', 'property' ,'occurs', 'retrieving', 'object', 'checked','true', 'returns','handled', 'work', 'function','existing', 'migrate', 'planning', 'release', 'replace', 'bit', 'careful', '{',');','properly', 'updating', 'fetch', 'rahul',';','on']
    for w in more_stop_words:
        stop_words.append(w)
    print("stop_words list contains "+str(len(stop_words))+" words")

    #making a string from various attributes of knowledge
    s =  a+" " +b
    
    print(s)
    doc = s.lower()
    
    #Making the test case optimised


    doc = doc.lower()
    doc = doc.replace(","," ")
    doc = doc.replace("'"," ")
    doc = doc.replace('"', " ")
    doc = doc.replace(":"," ")
    doc = doc.replace("="," ")

    # Step 1 : Find total words in the document
    total_words = doc.split()
    total_word_length = len(total_words)
    print(total_word_length)

    # Step 2 : Find total number of sentences
    total_sentences = tokenize.sent_tokenize(doc)
    total_sent_len = len(total_sentences)
    print(total_sent_len)

    # Step 3: Calculate TF for each word
    tf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words:
            if each_word in tf_score:
                tf_score[each_word] += 1
            else:
                tf_score[each_word] = 1
    print(tf_score)

    # Dividing by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())

    print(tf_score)
    # Check if a word is there in sentence list
    def check_sent(word, sentences): 
        final = [all([w in x for w in word]) for x in sentences] 
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
        return int(len(sent_len))


    # Step 4: Calculate IDF for each word
    idf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words:
            if each_word in idf_score:
                idf_score[each_word] = check_sent(each_word, total_sentences)
            else:
                idf_score[each_word] = 1

    # Performing a log and divide
    idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())

    print(idf_score)
    # Step 5: Calculating TF*IDF
    tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()} 
    print(tf_idf_score)
    # Get top N important words in the document
    n = len(tf_idf_score)
    tf_idf_score = dict(sorted(tf_idf_score.items(), key = itemgetter(1), reverse = True)[:n]) 
    
    print()
    print()
    print("The tags for the given doc are:")
    
    result=[]
    c = 10
    for k in tf_idf_score.keys():
        k = k.upper()
        result.append(k)

    print(result)


    #making a dictionary for saving to database
    tags = {"tag" : []}

    for k in tf_idf_score.keys():
        k = k.upper()
        k = k.replace(",","")
        if not(k.isnumeric()) and k not in tags["tag"] and k.upper() not in tags["tag"] :
            tags["tag"].append(k)
        
        if len(tags["tag"])==3:
            break

     

    #For sending tags to database
    print(tags)
    global taggs
    taggs = tags
    print("global",taggs)   
    global finaltags
    finaltags=taggs["tag"]
    print("Tags",tags)
    global uniqueId
    print("this is uniqueId",uniqueId)
    print("this is finaltags",finaltags)
    conn=MongoClient()
    db=conn.knowledgeplatform
    collection=db.knowledge
    db.knowledge.update({'ID':uniqueId},{"$set": {'tags':finaltags}})



def jira(request):
    conn = mod4.connect("User=knowledgeplatform64@gmail.com;APIToken=2Fu16O562HbjCKbqIoGqE126 ;Url=https://knowledgeplatform64.atlassian.net")
    # cur = conn.execute("SELECT Key, Name FROM Projects")
    cur = conn.execute("SELECT Summary, Id, Description, AssigneeDisplayName FROM Issues")
    rs = cur.fetchall()
    d = {'Summary':[], 'BugId':[], 'Description':[], 'Assignee':[]}
    for row in rs:
        print(row)
    for i in rs:
        d['Summary'].append(i[0]);
        d['BugId'].append(i[1]);
        d['Description'].append(i[2])
        d['Assignee'].append(i[3])
    print(d)
    return render(request,"jira.html")


def salesforce(request):
    conn = mod3.connect("User='af@gcet.com';Password='admin123';Security Token='G7wSptekqNONY1L3hBSs9T27';") #here we import salesforce by name of mod3
    cur = conn.execute("SELECT Name,BillingState, Id FROM Account")
    rs = cur.fetchall()
    print(rs)
    for row in rs:
        print(row)
    
    global d2
    d2 = {'name':[], 'billingState':[], 'id' : []}

    for t in rs:
        print("Hello")
        d2['name'].append(t[0]);
        d2['billingState'].append(t[1]);
        d2['id'].append(t[2])
    
    mlt=zip(d2['name'],d2['billingState'],d2['id'])
    context={'mlt':mlt,}

    return render(request, 'salesforcedisplay.html',context)          


#This function is used to display the tickets that are raised in salesforce
def salesforcedisplay(request):
    mlt=zip(d2['name'],d2['billingState'],d2['id'])
    context={'mlt':mlt,}
    return render(request, 'salesforcedisplay.html',context)




   