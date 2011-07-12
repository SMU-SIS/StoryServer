'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
from django import http

from tictactoe import views
#from tictactoe import TicTacToe

class Test_TicTacToe_Views(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def test_TicTacToe_Views(self):
        request = http.HttpRequest()
        request.path = 'TEST'
            
        #views.delete_app(request, app.key().id())
        #numApps = models.App.all().count()
        #self.assertEqual(0, numApps)
 
        views.index(request)
        views.get_supported_games(request)
        views.get_new_board(request)
        views.get_input_from_request(request)
        views.is_board_valid(request)
        views.game_status(request)
        views.get_next_move(request)
        views.is_move_valid(request)

   
 
                                  
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
