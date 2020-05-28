import React from 'react';

export class WordDisplay extends React.Component {
    constructor(props) {
        super(props);
        this.state = { guesses: this.props.guesses }

        this.convertArrayToUnderscored = this.convertArrayToUnderscored.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.guesses != this.props.guesses) {
            this.setState({ guesses: nextProps.guesses });
        }
    }

    convertArrayToUnderscored() {
        var result = "";
        var new_char;
        this.state.guesses.forEach(letter => {
            if (letter === null) {
                new_char = "_";
            } else {
                new_char = letter;
            }
            result += new_char;
        });
        return result;
    }

    render() {
        const hangmanWordStyling = {
            letterSpacing: "0.2em",
        };
        return <div>
            <h2 style={hangmanWordStyling}>{this.convertArrayToUnderscored(this.state.guesses)}</h2>
        </div>;
    }
}