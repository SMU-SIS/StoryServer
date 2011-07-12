'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
from django import http

from tournament import models
from tournament import views
from tournament.forms import AppForm, TournamentHeatForm

class Test_Tournament_Views(unittest.TestCase):

    def setUp(self):
        self.user = models.User(user_id ='Tom').save()
        self.competition = models.Competition(owner=self.user,
                                         name = 'Test Competition', 
                                         password = 'TEST',
                                         supportedGameTypes = ['TicTacToe']
                                         ).save()
                                         
        self.tournament = models.Tournament(owner = self.user,
                                      competition = self.competition, 
                                      gameType = 'TicTacToe'
                                      ).save()
    
    def tearDown(self):
        for x in models.User.all(): x.delete()
        for x in models.Competition.all(): x.delete()
        for x in models.Tournament.all(): x.delete()
        for x in models.App.all(): x.delete()
        
    def test_add_and_delete_app(self):
        request = http.HttpRequest()
        request.path = 'TEST'
        
        result = models.App.all().count()
        self.assertEqual(0, result) 
        views.add_app(request)
        result = models.App.all().count()
        self.assertEqual(1, result) 
        
        app = models.App.all().get()
        template, params = views.check_app(request, app.key().id())
        self.assertEqual('check_app', template)
        self.assertTrue('get_next_move_result' in params)
        self.assertTrue('app' in params)
        self.assertTrue('game_status_result' in params)
        
        views.delete_app(request, app.key().id())
        numApps = models.App.all().count()
        self.assertEqual(0, numApps)
                          
        
    def test_run_round(self):
        numPlayers = 2;
        #for player in range(numPlayers):
        appXID = models.App(name='TestApp 1', url='DEFAULT_TICTACTOE')
        appXID.put()
        appOID = models.App(name='TestApp 2', url='DEFAULT_TICTACTOE')
        appOID.put()       
        
        tournamentHeat = models.TournamentHeat(name='TestTournament', tournament=self.tournament)
        tournamentHeat.put()
        #tournamentHeat = models.TournamentHeat.all().get()
        numGames = models.Game.all().count()
        self.assertEqual(0, numGames)
                
        result = views.run_round(tournamentHeat) 
        self.assertTrue('points' in result)
        self.assertTrue('losses' in result)
        self.assertTrue('appNames' in result)
        self.assertTrue('matchResults' in result)
        self.assertTrue('appIDs' in result)
        self.assertTrue('ids' in result)
        
        self.assertEqual(numPlayers, len(result['points']))

        numGames = models.Game.all().count()
        self.assertEqual(2, numGames)
        
        request = http.HttpRequest()
        request.path = 'TEST'
        
        #Text result views
        result = views.run_tournament_heat(request,tournamentHeat.key().id())
        result = views.live_run_tournament_heat(request, tournamentHeat.key().id())
        result = views.view_game_result(request, tournamentHeat.key().id(), appXID.key().id(), appOID.key().id())
       
        #Template Methods
        template, params = views.view_heat_result(request, tournamentHeat.key().id())
        template, params = views.edit_entity(request, tournamentHeat.key().id(), c = models.TournamentHeat, useForm = TournamentHeatForm)  
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
