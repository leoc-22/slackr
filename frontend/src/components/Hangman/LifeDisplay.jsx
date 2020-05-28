import React from 'react';

export class LifeDisplay extends React.Component {
    constructor(props) {
        super(props);
        this.state = { lives: this.props.lives }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.lives != this.props.lives) {
            this.setState({ lives: nextProps.lives });
        }
    }

    getImageFromLives(livesLeft) {
        var imgURL;
        // all credit for images goes to wikipedia
        switch (livesLeft) {
            case 0:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Hangman-6.png/60px-Hangman-6.png";
                break;
            case 1:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Hangman-5.png/60px-Hangman-5.png";
                break;
            case 2:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hangman-4.png/60px-Hangman-4.png";
                break;
            case 3:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Hangman-3.png/60px-Hangman-3.png";
                break;
            case 4:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hangman-2.png/60px-Hangman-2.png";
                break;
            case 5:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hangman-1.png/60px-Hangman-1.png";
                break;
            case 6:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hangman-0.png/60px-Hangman-0.png";
                break;
            default:
                imgURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hangman-0.png/60px-Hangman-0.png";
        }
        return imgURL;
    }

    render() {
        return <div>
            <p>Lives left: {this.state.lives}</p>
            <img src={this.getImageFromLives(this.state.lives)} alt={"Hangman display with " + this.state.lives + " lives left"} />
        </div>
    }
}