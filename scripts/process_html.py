from bs4 import BeautifulSoup
import re
import random


def main():
    f = open('output_1_5676.csv','w')
    delim = '~'
    f.write('game_id'+delim+'show_num'+delim+'year'+delim+'round'+delim+'category'+
            delim+'clue_num'+delim+'response'+delim+'text'+delim+'value'+
            delim+'dd_wager'+
            delim+'clue_order'+delim+'incorrect'+delim+'id\n')
    # Get random sampling from 1 to 5676 (not including 3576, which was the
    # second half of 3575)
    # Note that clue values doubled from show number 3966 on
    games = random.sample(range(1,5676),100)   
    _id = 1
    
    for num in range(1,5677):
        if num == 3576:
            continue
        with open("../data/showgame.php@game_id="+str(num)+".html",encoding='utf8') as fp:            
            soup = BeautifulSoup(fp, 'lxml')
            
        
        # game metadata
        game_id = str(num)        
##        print(game_id)
        show_title = soup.find(id='game_title')

        # Check for italics in game title ("super jeopardy") Super hacky
        childCount=0
        for part in show_title.descendants:
            childCount = childCount + 1        
        if childCount>2:            
            show_title = re.sub('<i.*/i> ','',str(show_title.contents[0]))
            show_num = re.search('#\d+',show_title).group()
            show_num = show_num[1:]
            show_year = show_title[-9:-5]
        else: 
            show_title = str(show_title.string)
            show_num = re.search('\d+',show_title).group()
            show_year = show_title[-4:]
        
        # categories
        cat_tags = soup.find_all('td',class_='category_name')
        categories = []
        for tag in cat_tags:
            cat_text = ''            
            if len(tag.contents) > 1:                
                cat_str = ''
                for part in tag.strings:
                    cat_str = cat_str + part                        
                cat_text = str(cat_str)
            elif tag.a:
                # it's a movie category
                mov_cat_text = ''
                for s in tag.a.strings:
                    mov_cat_text = mov_cat_text + str(s) 
                cat_text = mov_cat_text
            elif tag.em:
                # it's underline category
                em_cat_text = ''
                for s in tag.em.strings:
                    em_cat_text = em_cat_text + str(s)
                cat_text = em_cat_text
            else: 
                cat_text = str(tag.string)
            categories.append(cat_text)
        

##        # Set up final jeopardy
##        fj = soup.find('table', class_='final_round')
##        fj_category = fj.find(class_='category_name').string
        
        # Set up regular clues
        clues = soup.find_all('td', class_='clue')
        
        i = 1        
        for clue in clues:
            fj = False
            tb = False
            blank = False
            incorrect = -1
            clue_str = game_id+delim+show_num+delim+show_year+delim
##            print(clue_str+" "+str(i))
            i = i+1

            if clue.find(id='clue_FJ'):
                fj = True
            elif clue.find(id='clue_TB'):
                tb = True

            ## Parse javascript for correct clue response            
            if not fj and not tb:
                # check for blank
                if len(clue.contents)==1:
                    blank = True
                else:
                    js = clue.find('div')                    
                    js_str = js['onmouseover']
                    ## Get clue id, which includes round, category, and clue num
                    ## e.g. clue_J_2_1                
                    clue_id = re.search(r'clue_\w+_\d_\d', js_str).group().split('_')
                    clue_round = str(clue_id[1])
                    # get categories by indexing array, need to decrement cat num
                    # and then add 6 to get double jeopardy
                    # fj_category is at index 12
                    if clue_round=='J':
                        clue_cat = str(categories[int(clue_id[2])-1])
                    elif clue_round=='DJ':                        
                        clue_cat = str(categories[int(clue_id[2])+5])               
                    else:
                        clue_cat = 'n/a'
                        
                    clue_num = str(clue_id[3])
    ##                print(clue_round+" "+clue_cat+" "+clue_num)                    
                    clue_str = clue_str + clue_round+delim+clue_cat+delim+clue_num+delim

                    ## Get clue response from js
                    ## (\w*|\s|\'|\.)+
                    testSoup = BeautifulSoup(js_str, 'lxml')
                    clue_response = testSoup.find(class_='correct_response')
                    if len(clue_response.contents) > 1:
                        text_str = ''
                        for part in clue_response.strings:
                            text_str = text_str + part                        
                        clue_response = str(text_str)
                    elif clue_response.i:
                        # it's an italic response
                        italic_clue_resp = ''
                        for s in clue_response.i.strings:
                            italic_clue_resp = italic_clue_resp + str(s) 
                        clue_response = italic_clue_resp 
                    else: 
                        clue_response = str(clue_response.string)

                    # Determine difficulty of question by counting number of wrong responses
                    # or triple stumpers
                    clue_incorrect = testSoup.find_all(class_='wrong')                    
                    incorrect = len(clue_incorrect)
                    tripleStumper = testSoup.find(class_='wrong', string = 'Triple Stumper')
                    # Hardest, triple stumper, no guesses
                    if not tripleStumper == None:
                        if incorrect == 1:                            
                            incorrect = 3 # No one guessed
                        elif incorrect == 4:
                            incorrect = 6 # Everyone guessed wrong
                        elif incorrect == 3:
                            incorrect = 5 # Two people guessed wrong, last person didn't guess                            
                        elif incorrect == 2:
                            incorrect = 4 # One person guessed wrong, no one else guessed

                    # These cases are correctly contained in the incorrect count
                    # Two people guessed wrong, last person got it right
                    # One person guessed wrong, next person got it right
                    #The last case is first person got it right                    
                    

##                    clue_response = re.search(r'onse">.*</em',js_str).group()[6:-4]
##                    # clean clue response of backslashes
##                    clue_response = clue_response.replace('\\','')
##                    # clean clue response of italics
##                    clue_response = clue_response.replace('<i>','')
##                    clue_response = clue_response.replace('</i>','')
##    ##                print(clue_response)
            elif fj:
                # it's final jeopardy
##                fj = True
                clue_round = 'FJ'
                clue_cat = categories[12]
                clue_num = '-1'

                clue_str = clue_str + clue_round+delim+clue_cat+delim+clue_num+delim

                # need to go to parent, then previous sibling, then find the div
                par = clue.find_parent()
                sib = par.find_previous_sibling()
                div = sib.find('div')
                js_str = div['onmouseover']
                
                ## Get clue response from js
                ## (\w*|\s|\'|\.)+
                testSoup = BeautifulSoup(js_str, 'lxml')
                clue_response = testSoup.find(class_='\\"correct_response\\"')
                if len(clue_response.contents) > 1:
                    text_str = ''
                    for part in clue_response.strings:
                        text_str = text_str + part                        
                    clue_response = str(text_str)
                elif clue_response.i:
                    text_str = ''
                    for part in clue_response.i.strings:
                        text_str = text_str + part                        
                    clue_response = str(text_str)
                else: 
                    clue_response = str(clue_response.string)

                # Determine difficulty of question by counting number of wrong responses
                # or triple stumpers
                clue_incorrect = testSoup.find_all(class_='wrong')                    
                incorrect = len(clue_incorrect)
                # In FJ, there is no Triple Stumper designation, so the number of
                # wrong elements should equal the number who got it wrong
                
            else:
                #it's a tiebreaker
                clue_round = 'TB'
                clue_cat = categories[13]
                clue_num = '-1'

                clue_str = clue_str + clue_round+delim+clue_cat+delim+clue_num+delim

                # need to go to parent, then previous sibling, then find the div
                par = clue.find_parent()
                sib = par.find_previous_sibling()
                div = sib.find('div')
                js_str = div['onmouseover']
                
                ## Get clue response from js
                ## (\w*|\s|\'|\.)+
                testSoup = BeautifulSoup(js_str, 'lxml')
                clue_response = testSoup.find(class_='\\"correct_response\\"')
                if len(clue_response.contents) > 1:
                    text_str = ''
                    for part in clue_response.strings:
                        text_str = text_str + part                        
                    clue_response = str(text_str)
                else: 
                    clue_response = str(clue_response.string)

                # Determine difficulty of question by counting number of wrong responses
                # or triple stumpers
                clue_incorrect = testSoup.find_all(class_='wrong')                    
                incorrect = len(clue_incorrect)         

                
                    
            # clean clue response of backslashes
            
            clue_response = clue_response.replace('\\','')
            # clean clue response of italics
            clue_response = clue_response.replace('<i>','')
            clue_response = clue_response.replace('</i>','')                

            # clean out hyperlinks in responses
            

            clue_str = clue_str + clue_response + delim
            
            ## Get clue text
            clue_text = clue.find(class_='clue_text')                
            # if there are more tags inside the clue text, just build
            # the string manually, otherwise, convert the NavigableString
            # to unicode

            if not blank:                
                if len(clue_text.contents) > 1:                    
                    text_str = ''                    
                    for part in clue_text.strings:  
                        text_str = text_str + part                        
                    clue_text = str(text_str)
                elif clue_text.a:
                    # it's a movie clue
                    mov_clue_text = ''
                    for s in clue_text.a.strings:
                        mov_clue_text = mov_clue_text + str(s) 
                    clue_text = mov_clue_text                    
                else:
                    clue_text = str(clue_text.string)

                if 'Clue Crew' in clue_text:
                    clue_text = re.sub(r'\(.*\) +','', clue_text)
                    
                clue_str = clue_str + clue_text +delim           
            
                if not fj and not tb:
                    ## get clue value and wager, if applicable
                    clue_value = clue.find(class_='clue_value')
                    if clue_value:
                        reg_val = clue_value.string[1:]
                        clue_str = clue_str + reg_val + delim + '-1' + delim
                    elif clue.find(class_='clue_value_daily_double'):
                        # daily double
                        # Parse and save the wager amount
                        dd_wager = clue.find(class_='clue_value_daily_double').string
                        dd_wager = dd_wager[5:]
                        dd_wager = re.sub(',','',dd_wager)
                        # then find the expected value based off the location
                        
                        values = [-1, 100,200,300,400,500]
                        expected_value = values[int(clue_num)]
                        # Double expected value if DJ
                        if clue_round == 'DJ':
                            expected_value = expected_value * 2    
                            
                        # need to account for value change past show 3966
                        if int(show_num) >= 3966:
                            expected_value = expected_value * 2    

                        clue_str = clue_str + str(expected_value) + delim + dd_wager + delim
    ##                elif clue.find(id='clue_FJ'):
    ##                    print('FJ')
                    else:
                        # it was never chosen
                        clue_str = clue_str + '-1' + delim + '-1' + delim

                    ## get clue order number
                    clue_order_num = clue.find(class_='clue_order_number')
    ##                if clue_order_num:
                    clue_str = clue_str + clue_order_num.string
    ##                else:
    ##                    print('FJ')                
                else:
                    clue_str = clue_str +'-1'+delim+'-1'+delim+'-1'

                clue_str = clue_str + delim + str(incorrect) + delim + str(_id)
                _id = _id + 1
                
                # write clue string to file
                try:
                    f.write(clue_str+'\n')
                except UnicodeEncodeError:
                    pass
        # write fj to file
##        f.write(fj_str+'\n')
        
    f.close()
    
if __name__ == "__main__":
    main()
