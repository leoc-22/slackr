import React from 'react';

export class IncorrectLetterDisplay extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            incorrectLetters: this.props.incorrectLetters,
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.incorrectLetters != this.props.incorrectLetters) {
            this.setState({ incorrectLetters: nextProps.incorrectLetters });
        }
    }

    convertArrayToText(array) {
        var result = array.sort().join(', ');
        return result;
    }

    render() {
        return <div>
            <h3>Incorrect Guesses: </h3><h5>{this.convertArrayToText(this.state.incorrectLetters)}</h5>
        </div>
    }
}