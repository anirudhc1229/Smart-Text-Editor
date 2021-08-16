# DRIVE LINK: https://drive.google.com/drive/folders/1B5hVRZLXRYlT0GE9j3VL3CxKP6q0Okq_?usp=sharing

import random
import math
import string
import statistics
import numpy

import smtplib
import requests
import googlesearch
import concurrent.futures

from PyDictionary import PyDictionary
from bs4 import BeautifulSoup


# presentation4cs@gmail.com
# giveMeA-Plus


class Word:

    def __init__(self, orig):
        self.orig = orig
        self.punct = self.findPunct()
        self.cap = self.findCap()
        self.standard = self.findStandard()

    def findPunct(self):
        startPunct = ""
        endPunct = ""
        hasPunct = False
        for char in self.orig:
            if char in string.punctuation:
                startPunct += char
            else:
                break
        reverseOrig = self.orig[::-1]
        for char in reverseOrig:
            if char in string.punctuation:
                endPunct += char
            else:
                break
        endPunct = endPunct[::-1]
        return [startPunct, endPunct]

    def findCap(self):
        cap = 0
        myWord = self.orig.replace(self.punct[0], "").replace(self.punct[1], "")
        if myWord[0].isupper():
            cap = 1
        if myWord.isupper():
            cap = 2
        return cap

    def findStandard(self):
        standard = self.orig.lower().replace(self.punct[0], "").replace(self.punct[1], "")
        return standard

    def getOrig(self):
        return self.orig
    def getPunct(self, loc):
        if loc == "start":
            return self.punct[0]
        if loc == "end":
            return self.punct[1]
    def getCap(self):
        return self.cap
    def getStandard(self):
        return self.standard


inp = []
inpFile = ""
myDict = []


def getInp():

    global inp, inpFile

    inpFile = input("\nEnter name of file: ")

    while True:
        try:
            with open(inpFile) as data:
                inp = data.read().split()
        except:
            inpFile = input("ERROR: File not found\n\nEnter name of file: ")
        else:
            break

    print("\n" + text())


def wordCharCount():

    global inp

    wordCount = len(inp)
    charCount = 0
    for word in inp:
        charCount += len(word)
    charAndSpace = charCount + wordCount - 1

    print("\nWords: " + str(wordCount) +
          "\nCharacters: " + str(charAndSpace) +
          "\nCharacters (excluding spaces): " + str(charCount))


def findAndReplace():

    global inp, inpFile

    while True:

        find = input("\nEnter word to find, or click ENTER to terminate: ").lower()
        if find == "":
            break
        replace = input("\nEnter word to replace with: ")
        ask = tryExInt("\nMatch case?\n\t"
                        "1: Yes\n\t"
                        "2: No\n")
        found = 0

        for i in range(len(inp)):
            myWord = Word(inp[i])
            if myWord.getStandard() == find:
                if ask == 1:
                    inp[i] = myWord.getPunct("start") + matchCap(replace, myWord.getCap()) + myWord.getPunct("end")
                else:
                    inp[i] = myWord.getPunct("start") + replace + myWord.getPunct("end")
                found += 1

        print("\n" + text())
        if found == 0:
            print("\nNo instances of '" + find + "' were found.")
        elif found == 1:
            print("\n1 instance of '" + find + "' replaced with '" + replace + "'.")
        else:
            print("\n" + str(found) + " instances of '" + find + "' replaced with '" + replace + "'.")


def smartReplace():

    global inp

    pyDict = PyDictionary()

    while True:

        find = input("\nEnter word to find, or click ENTER to terminate: ").lower()
        if find == "":
            break

        while True:
            syn = pyDict.synonym(find)
            if syn == None:
                find = input("\nERROR: Word not compatible with Smart Replace\n\nEnter word to find: ")
            else:
                break

        options = []
        print("\nChoose word to replace with:")
        for i in range(len(syn)):
            if not " " in syn[i]:
                print("\t" + str(i + 1) + ": " + syn[i])
                options.append(syn[i])

        replace = options[tryExInt("\n") - 1]
        percent = tryExInt("\nEnter an approximate percentage of occurrences of '" + find +
                               "' to replace with '" + replace + "': ")

        found = 0
        candidates = []
        for i in range(len(inp)):
            myWord = Word(inp[i])
            if myWord.getStandard() == find:
                candidates.append(i)
                found += 1

        numReplace = math.ceil(percent / 100 * found)

        for i in range(numReplace):
            ind = random.choice(candidates)
            myWord = Word(inp[ind])
            inp[ind] = myWord.getPunct("start") + matchCap(replace, myWord.getCap()) + myWord.getPunct("end")

        print("\n" + text())
        if found == 0:
            print("\nNo instances of '" + find + "' were found.")
        else:
            print("\n" + str(numReplace) + " of " + str(found) +
                  " instances of '" + find + "' replaced with '" + replace + "'.")


def spellCheck():

    global inp, myDict

    with open("Dictionary.txt") as data:
        theDict = data.read().split("\n")
    for i in range(len(theDict)):
        theDict[i] = theDict[i].lower()

    good = True

    print("\nScanning document...")

    for i in range(len(inp)):
        myWord = Word(inp[i])
        lastWord = Word(inp[i - 1])
        lastPunct = lastWord.getPunct("end")
        if not (myWord.getStandard() in theDict) and not (myWord.getStandard() in myDict) \
                and not ((myWord.getCap() == 1) and not (len(lastPunct) > 0 and lastPunct[-1] == ".")) \
                and not ("'" in list(myWord.getStandard())):
            bestMatch = didYouMean(myWord.getStandard())
            ask = tryExInt("\nIt appears the word '" + myWord.getStandard() + "' is either misspelled or undefined. "
                                 "Did you mean: '" + bestMatch + "'?\n\t"
                           "1: Replace with suggestion\n\t"
                           "2: Edit\n\t"
                           "3: Add to dictionary\n\t"
                           "4: Ignore\n")
            if ask == 1:
                inp[i] = myWord.getPunct("start") + matchCap(bestMatch, myWord.getCap()) + myWord.getPunct("end")
                print("\n" + text())
            elif ask == 2:
                fix = input("\nEnter the word to replace '" + myWord.getStandard() + "' with: ")
                inp[i] = myWord.getPunct("start") + matchCap(fix, myWord.getCap()) + myWord.getPunct("end")
                print("\n" + text())
            elif ask == 3:
                myDict.append(myWord.getStandard())
                print("\n'" + myWord.getStandard() + "' has been added to the dictionary.")
            good = False
            print("\nScanning document...")

    if good:
        input("\nNo spelling errors found.\n\nClick ENTER to continue: ")
    else:
        input("\nNo spelling errors remain.\n\nClick ENTER to continue: ")


def didYouMean(myWord):

    with open("Dictionary.txt") as data:
        theDict = data.read().split("\n")

    theDict = list(filter(lambda dictWord :
                          (len(dictWord) < len(myWord) + 2) and (len(dictWord) > len(myWord) - 2), theDict))
    for i in range(len(theDict)):
        theDict[i] = theDict[i].lower()

    ratios = []
    for dictWord in theDict:
        ratios.append(levenDistRatio(myWord, dictWord))

    return theDict[ratios.index(max(ratios))]


def grammarCheck():

    good1 = aVsAnCheck()
    good2 = capCheck()
    good3 = thereCheck()
    good4 = conjugCheck()

    if good1 and good2 and good3 and good4:
        input("\nNo grammar errors found.\n\nClick ENTER to continue: ")
    else:
        input("\nNo grammar errors remain.\n\nClick ENTER to continue: ")


def aVsAnCheck():

    global inp

    vowels = ["a", "e", "i", "o", "u"]
    good = True

    for i in range(len(inp) - 1):
        myWord = Word(inp[i])
        nextWord = Word(inp[i + 1])
        if (myWord.getStandard() == "a") and (nextWord.getStandard()[0] in vowels):
            fixGrammar(myWord, "an", good)
        elif (myWord.getStandard() == "an") and (nextWord.getStandard()[0] not in vowels):
            fixGrammar(myWord, "a", good)

    return good


def capCheck():

    global inp

    good = True

    for i in range(len(inp) - 1):
        myWord = Word(inp[i])
        lastWord = Word(inp[i - 1])
        lastPunct = lastWord.getPunct("end")
        endingPunct = [".", "!", "?"]
        if ((i == 0) or (len(lastPunct) > 0 and lastPunct[-1] in endingPunct) or myWord.getStandard() == "i") \
                and (myWord.getCap() == 0):
            ask = tryExInt("\nIt appears the word '" + myWord.getStandard() + "' should be capitalized.\n\t"
                            "1: Edit\n\t"
                            "2: Ignore\n")
            if ask == 1:
                inp[i] = myWord.getPunct("start") + matchCap(myWord.getStandard(), 1) + myWord.getPunct("end")
                print("\n" + text())

            good = False

    return good


def thereCheck():

    global inp

    good = True

    for i in range(len(inp)):
        myWord = Word(inp[i])
        if (myWord.getStandard() == "their" or myWord.getStandard() == "they're") and (len(myWord.getPunct("end")) > 0):
            fixGrammar(myWord, "there", good)

    return good


def conjugCheck():

    presConjug = {"i": "am", "you": "are", "he": "is", "she": "is", "we": "are", "they": "are",
                  "this": "is", "that": "is", "it": "is"}
    pastConjug = {"i": "was", "you": "were", "he": "was", "she": "was", "we": "were", "they": "were",
                  "this": "was", "that": "was", "it": "was"}
    good = True

    for i in range(len(inp)):
        myWord = Word(inp[i])
        lastWord = Word(inp[i - 1])
        if (myWord.getStandard() in presConjug.values()) and (lastWord.getStandard() in presConjug.keys()) \
                and (presConjug.get(lastWord.getStandard()) != myWord.getStandard()):
            fixGrammar(myWord, presConjug.get(lastWord.getStandard()), good)
        elif (myWord.getStandard() in pastConjug.values()) and (lastWord.getStandard() in pastConjug.keys()) \
                and (pastConjug.get(lastWord.getStandard()) != myWord.getStandard()):
            fixGrammar(myWord, pastConjug.get(lastWord.getStandard()), good)

    return good


def fixGrammar(myWord, replace, good):

    global inp

    ask = tryExInt("\nIt appears the word '" + myWord.getStandard() +
                   "' should be replaced with '" + replace + "'.\n\t"
                   "1: Edit\n\t"
                   "2: Ignore\n")
    if ask == 1:
        inp[inp.index(myWord.getOrig())] = \
            myWord.getPunct("start") + matchCap(replace, myWord.getCap()) + myWord.getPunct("end")
        print("\n" + text())

    good = False


def plagCheck():

    global inpFile, sentenceSim

    print("\nScanning document...")

    with open(inpFile) as data:
        mySentences = data.read().replace("!", ".").replace("?", ".").split(".")

    simValues = []

    for mySentence in mySentences:
        sentenceSim = []
        urls = []
        NUM_URLS = 3
        for url in googlesearch.search(mySentence, tld='com', lang='en',
                                       num=NUM_URLS, start=0, stop=NUM_URLS, pause=2.0):
            urls.append(url)
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_URLS) as executor:
            results = list(executor.map(requests.get, urls))
        for result in results:
            urlSim = []
            soup = BeautifulSoup(result.content, 'html.parser')
            for p in soup.find_all("p"):
                urlSentences = p.get_text().replace("!", ".").replace("?", ".").split(".")
                for urlSentence in urlSentences:
                    urlSim.append(levenDistRatio(mySentence, urlSentence))
            if urlSim != []:
                sentenceSim.append(max(urlSim))
        if sentenceSim != []:
            simValues.append(max(sentenceSim))

    authenticity = 100 - (100 * statistics.mean(simValues))
    rating = ""
    if authenticity > 80:
        rating = "Excellent"
    elif authenticity > 70:
        rating = "Good"
    elif authenticity > 50:
        rating = "Fair"
    else:
        rating = ("LIKELY PLAGIARIZED")

    print("\nAuthenticity: " + "%.2f" % authenticity + "% [" + rating + "]")


def saveChanges():

    global inpFile

    ask = tryExInt("\nSave changes to file?\n\t"
                    "1: Save\n\t"
                    "2: Discard\n")

    if ask == 1:
        outFile = open(inpFile, 'w')
        outFile.write(text())
        print("\nSaved successfully to '" + inpFile + "'")


def emailShare():

    ask = tryExInt("\nShare text via email?\n\t"
                   "1: Yes\n\t"
                   "2: No\n")

    if ask == 1:

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        address = input("\nEnter your Gmail address: ")
        password = input("\nEnter your account pasword: ")

        while True:
            try:
                server.login(address, password)
            except:
                print("\nERROR: Incorrect Gmail address or password")
                address = input("\nEnter your Gmail address: ")
                password = input("\nEnter your account pasword: ")
            else:
                break

        sendTo = []
        recipient = " "
        while recipient != "":
            recipient = input("\nEnter recepient Gmail address, or click ENTER to stop selecting recipients: ")
            if recipient != "":
                sendTo.append(recipient)

        with open(inpFile) as data:
            message = data.read()

        while True:
            try:
                server.sendmail(address, sendTo, message)
            except:
                print("\nERROR: Recipient(s) not found")
                sendTo = []
                recipient = " "
                while recipient != "":
                    recipient = input("\nEnter recepient Gmail address, or click ENTER to stop selecting recipients: ")
                    if recipient != "":
                        sendTo.append(recipient)
            else:
                break

        sharedWith = ""
        for i in range(len(sendTo)):
            sharedWith += ("'" + sendTo[i] + "'")
            if i < len(sendTo) - 1:
                sharedWith += ", "

        print("\nContents of '" + inpFile + "' successfully shared with " + sharedWith + " via email.")
        server.quit()


def levenDistRatio(str1, str2):

    # NOTE: I'm not the original creator of this algorithm, it's a common string
    # comparison algorithm called the Levenshtein Distance. I used a variety of
    # different tutorials to create it, undertstand it, and slightly modify it
    # for my own usage.

    distChart = numpy.zeros((len(str1) + 1, len(str2) + 1))
    for s1 in range(len(str1) + 1):
        distChart[s1][0] = s1
    for s2 in range(len(str2) + 1):
        distChart[0][s2] = s2

    for s1 in range(1, len(str1) + 1):
        for s2 in range(1, len(str2) + 1):
            if str1[s1 - 1] == str2[s2 - 1]:
                distChart[s1][s2] = distChart[s1 - 1][s2 - 1]
            else:
                a = distChart[s1][s2 - 1]
                b = distChart[s1 - 1][s2]
                c = distChart[s1 - 1][s2 - 1]
                distChart[s1][s2] = min(a, b, c) + 1

    dist = distChart[len(str1)][len(str2)]
    return 1 - dist / max(len(str1), len(str2))


def text():

    global inp

    formatted = inp.copy()
    lineLen = 0

    for i in range(len(formatted)):
        lineLen += len(formatted[i])
        if lineLen > 180:
            formatted[i - 1] += "\n"
            lineLen = 0

    return " ".join(formatted)


def matchCap(str, num):

    matched = ""

    if num == 0:
        matched = str.lower()
    elif num == 1:
        matched = str[0].upper() + str[1:].lower()
    elif num == 2:
        matched = str.upper()

    return matched


def tryExInt(prompt):

  ask = input(prompt)

  while True:
    try:
      ask = int(ask)
    except:
      ask = input(prompt)
    else:
      break

  return ask


def main():

    input("\n~~~TextEditor.py~~~\nClick ENTER to continue: ")
    getInp()

    while True:

        tasks = [wordCharCount, 
                 findAndReplace, 
                 smartReplace, 
                 spellCheck, 
                 grammarCheck, 
                 plagCheck]
        
        task = tryExInt("\nTasks:\n\t"
                       "1: Word/Character Count\n\t"
                       "2: Find and Replace\n\t"
                       "3: Smart Replace\n\t"
                       "4: Spell Check\n\t"
                       "5: Grammar Check (BETA)\n\t"
                       "6: Plagiarism Detection (BETA)\n\t"
                       "7: Print Document\n\t"
                       "8: Finish\n")
        
        if task <= len(tasks):
            tasks[task - 1]()
        elif task == 7:
            print("\n" + text())
        else:
            saveChanges()
            emailShare()
            ask = tryExInt("\nEdit another file?\n\t"
                           "1: Yes\n\t"
                           "2: No\n")
            if ask == 1:
                getInp()
            else:
                break

main()
