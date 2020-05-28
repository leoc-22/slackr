import React from 'react';
import axios from 'axios';
import { TailSpin } from 'svg-loaders-react'
import { LifeDisplay } from './LifeDisplay';
import { WordDisplay } from './WordDisplay';
import { IncorrectLetterDisplay } from './IncorrectLetterDisplay';

export class HangmanGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            inProgress: false,
            guesses: [],
            lives: -1,
            incorrectLetters: [],
            channel_id: this.props.channel_id,
            token: this.props.token,
            current_hangman_id: this.props.current_hangman_id,
        }


        this.toggleOn = this.toggleOn.bind(this);
        this.checkActive = this.checkActive.bind(this);
        this.updateData = this.updateData.bind(this);
        this.timerCheckUpdated = this.timerCheckUpdated.bind(this);
        this.checkGameFinished = this.checkGameFinished.bind(this);
        this.getAnswer = this.getAnswer.bind(this);
        this.updateDataOnLastLife = this.updateDataOnLastLife.bind(this);
    }

    componentDidMount() {
        this.interval = setInterval(() => this.timerCheckUpdated(), 7500);

        if (this.checkActive()) {
            this.updateData();
        }

    }

    componentWillUnmount() {
        clearInterval(this.interval)
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.channel_id != this.props.channel_id) {
            this.setState({ lives: -1, inProgress: false });
        }
    }

    timerCheckUpdated() {
        console.log("Checking data")
        var initialState = this.state.inProgress;
        console.log("Initial state: " + initialState);
        // If game not in progress, check if the game has started
        if (!this.state.inProgress) {
            // Call /hangman/active
            var newState = this.checkActive();
            // check if the state has changed
            console.log("New state: " + newState);
            if (initialState !== newState) {
                // the state has changed... get the data
                this.updateData();
            }
        } else {
            // the game is already in progress
            // check for new data
            if (this.state.lives === 1) {
                // the game may have finished but we are unaware
                this.updateDataOnLastLife();
            } else {
                this.updateData();
            }

        }
        console.log("Updated guesses:" + this.state.guesses);
    }

    toggleOn() {
        console.log("Game toggled on");
        this.setState({ inProgress: true });
    }

    checkActive() {
        var token = this.props.token;
        var channel_id = this.props.channel_id;
        var in_progress = this.state.inProgress;
        axios
            .get('/hangman/active', {
                params: {
                    token,
                    channel_id,
                },
            })
            .then(({ data }) => {
                if (data.in_progress === true) {
                    this.setState({
                        inProgress: true,
                    });
                    in_progress = true;
                    console.log("New state after checking... " + this.state.inProgress);
                    return true;
                }
            }).catch((err) => { });
        return in_progress;
    }

    updateDataOnLastLife() {
        var token = this.props.token;
        var channel_id = this.props.channel_id;
        axios
            .get('/hangman/details', {
                params: {
                    token,
                    channel_id,
                },
            })
            .then(({ data }) => {
                const { lives, guesses, incorrect_guesses, current_hangman_id } = data;
                this.setState({
                    lives: lives,
                    guesses: guesses,
                    incorrectLetters: incorrect_guesses,
                    current_hangman_id: current_hangman_id,
                })
                this.checkGameFinished(guesses);
            }).catch((err) => {
                this.setState({ lives: 0 });
                this.checkGameFinished(this.state.guesses, true);
            });
    }


    updateData() {
        var token = this.props.token;
        var channel_id = this.props.channel_id;
        var return_list = [];
        var return_data = {};
        axios
            .get('/hangman/details', {
                params: {
                    token,
                    channel_id,
                },
            })
            .then(({ data }) => {
                const { lives, guesses, incorrect_guesses, current_hangman_id } = data;
                this.setState({
                    lives: lives,
                    guesses: guesses,
                    incorrectLetters: incorrect_guesses,
                    current_hangman_id: current_hangman_id,
                })
                this.checkGameFinished(guesses, false);
            }).catch((err) => {
                this.checkGameFinished(this.state.guesses, false);
            });
    }



    checkGameFinished(guesses, definitelyFinished) {
        if (!guesses.includes(null)) {
            // the game has finished
            this.setState({ inProgress: false, lives: -1 });
            alert("You won! Good job!")
        } else if (this.state.lives === 0 || definitelyFinished === true) {
            this.setState({ inProgress: false, lives: -1 });
            this.getAnswer();
        }
    }

    getAnswer() {
        var token = this.props.token;
        var channel_id = this.props.channel_id;
        var current_hangman_id = this.state.current_hangman_id;
        axios.get('/hangman/answer', {
            params: {
                token,
                channel_id,
                current_hangman_id,
            },
        })
            .then(({ data }) => {
                alert("You lost! The word was: " + data.answer);
            })
            .catch((err) => {
                alert("You lost!\nDue to an error the correct answer could not be retrieved.");
            });
    }

    render() {
        if (this.state.inProgress) {
            if (this.state.lives === -1) {
                return <div>
                    <h2>Loading...</h2>
                    <TailSpin />
                </div>
            } else {
                return <div>
                    <WordDisplay guesses={this.state.guesses} />
                    <LifeDisplay lives={this.state.lives} />
                    <IncorrectLetterDisplay incorrectLetters={this.state.incorrectLetters} />
                </div>
            }

        } else {
            return <div>
                <h3>Game not in progress... Type `/hangman` to start!</h3>
            </div>
        }

    }
}
