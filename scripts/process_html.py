from bs4 import BeautifulSoup
import re
import random


def main():
    f = open('output_5401_5653.csv','w')
    f.write('game_id|show_num|year|round|category|clue_num|response|text|value|clue_order\n')
    # Get random sampling from 1 to 5653 (not including 3576, which was the
    # second half of 3575)
    # games = random.sample(range(1,5653),25)   
    
    for num in range(5401,5654):        
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
            fj = False;
            tb = False;
            blank = False;
            clue_str = game_id+'|'+show_num+'|'+show_year+'|'
##            print(clue_str+" "+str(i))
            i = i+1

            if clue.find(id='clue_FJ'):
                fj = True
            elif clue.find(id='clue_TB'):
                tb = True;

            ## Parse javascript for correct clue response            
            if not fj and not tb:
                # check for blank
                if len(clue.contents)==1:
                    blank = True;
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
                    clue_str = clue_str + clue_round+'|'+clue_cat+'|'+clue_num+'|'

                    ## Get clue response from js
                    ## (\w*|\s|\'|\.)+
                    testSoup = BeautifulSoup(js_str, 'lxml')
                    clue_response = testSoup.find(class_='correct_response')
                    if len(clue_response.contents) > 1:
                        text_str = ''
                        for part in clue_response.strings:
                            text_str = text_str + part                        
                        clue_response = str(text_str)
                    else: 
                        clue_response = str(clue_response.string)

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
                clue_num = 'n/a'

                clue_str = clue_str + clue_round+'|'+clue_cat+'|'+clue_num+'|'

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
            else:
                #it's a tiebreaker
                clue_round = 'TB'
                clue_cat = categories[13]
                clue_num = 'n/a'

                clue_str = clue_str + clue_round+'|'+clue_cat+'|'+clue_num+'|'

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

                
                    
            # clean clue response of backslashes
            
            clue_response = clue_response.replace('\\','')
            # clean clue response of italics
            clue_response = clue_response.replace('<i>','')
            clue_response = clue_response.replace('</i>','')                

            # clean out hyperlinks in responses
            

            clue_str = clue_str + clue_response+'|'
            
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
                else: 
                    clue_text = str(clue_text.string)

                if 'Clue Crew' in clue_text:
                    clue_text = re.sub(r'\(.*\) +','', clue_text)
                    
                clue_str = clue_str + clue_text +'|'           
            
                if not fj and not tb:
                    ## get clue value for regular clues and placeholders for others
                    clue_value = clue.find(class_='clue_value')
                    if clue_value:
                        clue_str = clue_str + clue_value.string + '|'
                    elif clue.find(class_='clue_value_daily_double'):
                        # it might be a daily double
                        clue_str = clue_str + 'DD|'
    ##                elif clue.find(id='clue_FJ'):
    ##                    print('FJ')
                    else:
                        # it was never chosen
                        clue_str = clue_str + 'NC|'

                    ## get clue order number
                    clue_order_num = clue.find(class_='clue_order_number')
    ##                if clue_order_num:
                    clue_str = clue_str + clue_order_num.string
    ##                else:
    ##                    print('FJ')                
                else:
                    clue_str = clue_str +'n/a|n/a'
                    
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
