'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
from tictactoe import TicTacToe #ConnectFour class is currently in this file

#import urllib
#import datetime
#from google.appengine.api import urlfetch
#from google.appengine.api import memcache
#from time import sleep
#from xxx import models
#from xxx import views

class ConnectFourTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def _test_local_return(self):
        appurl = 'DEFAULT_TICTACTOE'
        function = 'get_new_board'
        result = TicTacToe.local_return(appurl, function, {})
        self.assertEqual(True, 'board' in result)
        
        function = 'is_board_valid'
        next_result = TicTacToe.local_return(appurl, function, result)
        if not next_result:
            self.assertTrue(False)
        
        function=='is_move_valid'
        d = {'board':'***/n***/n***', 'move':'X**/n***/n***'}
        result = TicTacToe.local_return(appurl, function, d)
        self.assertEqual(True, 'valid' in result)
        
    def _test_get_players(self):
        result = TicTacToe.get_players()
        self.assertEqual(True, len(result)>0)
        
    def _test_is_board_valid(self): 
        board = 'X**\n***\n**'
        self.assertEqual(False, TicTacToe.TicTacToe.is_board_valid(board)['valid'],'Board is too short')
        board = 'X**\n***\n****'
        self.assertEqual(False, TicTacToe.TicTacToe.is_board_valid(board)['valid'],'Board is too long')
        board = 'X**\n*******'
        self.assertEqual(False, TicTacToe.TicTacToe.is_board_valid(board)['valid'],'Board does not have 2 carriage returns')
        board = 'X**\n***\n*G*'
        self.assertEqual(False, TicTacToe.TicTacToe.is_board_valid(board)['valid'], 'Non-valid character \n'+board)
        board = 'X**\n***\n***'
        self.assertEqual(True, TicTacToe.TicTacToe.is_board_valid(board)['valid'], 'Should be valid \n'+board+' \n'+TicTacToe.TicTacToe.is_board_valid(board)['message'])

    def _test_game_status(self):
        board = '***\n***\n***'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('X', result['turn'], "Should be X's turn. \n"+board+" \n"+str(result))
        self.assertEqual('PLAYING', result['status'], "Should be plaing game.\n"+board+" \n"+str(result))
        
        board = 'X**\n***\n***'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('O', result['turn'], "Should be O's turn. \n"+board+" \n"+str(result))
        self.assertEqual('PLAYING', result['status'], "Should be plaing game.\n"+board+" \n"+str(result))
        
        board = 'XOX\nXOO\nOXX'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('O', result['turn'], "Should be O's turn. \n"+board+" \n"+str(result))
        self.assertEqual('TIE', result['status'], "Should be a tie.\n"+board+" \n"+str(result))
        
        board = 'XXX\nXOO\nOXO'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('O', result['turn'], "Should be O's turn. \n"+board+" \n"+str(result))
        self.assertEqual('X WON', result['status'], "Should be X WON.\n"+board+" \n"+str(result))
 
        board = 'X**\nXOO\nX**'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('O', result['turn'], "Should be O's turn. \n"+board+" \n"+str(result))
        self.assertEqual('X WON', result['status'], "Should be X WON.\n"+board+" \n"+str(result))
        
        board = 'XOX\nXO*\n*O*'
        result = TicTacToe.TicTacToe.game_status(board)
        self.assertEqual('X', result['turn'], "Should be X's turn. \n"+board+" \n"+str(result))
        self.assertEqual('O WON', result['status'], "Should be O WON.\n"+board+" \n"+str(result))
    
    def _test_is_move_valid(self):
        start = '***\n***\n***'
        move = 'X**\n***\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(True, result['valid'], 'Move should be valid.')
        
        start = '***\n***\n***'
        move = 'O**\n***\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(False, result['valid'], 'O should not have more than X.')
        
        start = 'X**\n***\n***'
        move = 'XO*\n***\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(True, result['valid'], 'Move should be valid.')

        start = 'X**\n***\n***'
        move = '*OX\n***\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(False, result['valid'], 'Move should fail since not based on start.')
 
        start = 'X**\n***\n***'
        move = 'X**\n***\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(False, result['valid'], 'Move should fail since no move made.')

        start = 'X**\n***\n***'
        move = 'XOX\n*O*\n***'
        result = TicTacToe.TicTacToe.is_move_valid(start, move)
        self.assertEqual(False, result['valid'], 'Move should fail for multiple changes.')
        
    def _test_get_next_move(self):
        player = TicTacToe.TicTacToe()
        board = player.get_new_board()['board']
        moves = []
        for i in range(9):
            #print board + '\n'
            move = player.get_next_move(board)['move']
            moves.append(move)
            status = player.game_status(move)
            self.assertEqual(True, player.is_move_valid(board, move)['valid'])
            if status['status']!='PLAYING': 
              break
            board=move

    def _test_round_robin(self):
        
        players = [TicTacToe.TicTacToe(), TicTacToe.CenterGrabTicTacToe(), TicTacToe.RandomTicTacToe(),TicTacToe.CenterGrabRandomTicTacToe(),TicTacToe.BottomUpTicTacToe(), TicTacToe.HunterTicTacToe()]
        players.append(TicTacToe.InvalidReturnTicTacToe())
        players.append(TicTacToe.LoopBackTicTacToe())
        #players.append(TicTacToe.NoReturnTicTacToe())
        
        points = {}
        losses = {}
        for i in range(len(players)): 
          points[i]=0
          losses[i]=0
        
        for x in range(len(players)):
          for y in range(len(players)):
            if x!=y:
              result = TicTacToe.TicTacToe.head_to_head(players[x], players[y], TicTacToe.TicTacToe())
              if 'X' in result: 
                points[x]+=1
                losses[y]+=1
              elif 'O' in result: 
                points[y]+=1
                losses[x]+=1 
              else:
                points[x]+=0.5
                points[y]+=0.5
        print '\n'
        for k in points: 
          print k, 'scored', points[k], 'points', losses[k],'losses',players[k].get_name()
    
 
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()