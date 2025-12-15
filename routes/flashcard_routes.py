"""
Flashcard Routes - API endpoints for spaced repetition flashcards
"""

from flask import Blueprint, request, jsonify
from services import FlashcardService

flashcard_bp = Blueprint('flashcards', __name__)
flashcard_service = FlashcardService()


@flashcard_bp.route('/generate', methods=['POST'])
def generate_flashcards():
    """Generate flashcards from content"""
    try:
        data = request.json
        
        result = flashcard_service.generate_flashcards(
            content=data.get('content', ''),
            num_cards=data.get('num_cards', 20),
            user_id=data.get('user_id'),
            deck_name=data.get('deck_name')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/from-quiz/<quiz_id>', methods=['POST'])
def create_from_quiz(quiz_id):
    """Create flashcards from quiz wrong answers"""
    try:
        data = request.json
        
        result = flashcard_service.create_from_quiz(
            quiz_id=quiz_id,
            user_id=data.get('user_id'),
            wrong_only=data.get('wrong_only', True)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/user/<user_id>/due', methods=['GET'])
def get_due_cards(user_id):
    """Get flashcards due for review"""
    try:
        limit = request.args.get('limit', 50, type=int)
        deck_id = request.args.get('deck_id')
        
        cards = flashcard_service.get_due_cards(
            user_id=user_id,
            limit=limit,
            deck_id=deck_id
        )
        
        return jsonify({'cards': cards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/<card_id>/review', methods=['POST'])
def review_card(card_id):
    """Submit flashcard review"""
    try:
        data = request.json
        
        quality = data.get('quality', 3)
        if quality < 0 or quality > 5:
            return jsonify({'error': 'Quality must be 0-5'}), 400
        
        result = flashcard_service.review_card(
            card_id=card_id,
            quality=quality,
            user_id=data.get('user_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/user/<user_id>/decks', methods=['GET'])
def get_user_decks(user_id):
    """Get all decks for a user"""
    try:
        decks = flashcard_service.get_user_decks(user_id)
        return jsonify({'decks': decks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/deck/<deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get a deck with its cards"""
    try:
        deck = flashcard_service.get_deck(deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        return jsonify(deck)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/deck', methods=['POST'])
def create_deck():
    """Create a new deck"""
    try:
        data = request.json
        
        result = flashcard_service.create_deck(
            name=data.get('name'),
            description=data.get('description'),
            user_id=data.get('user_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/deck/<deck_id>/card', methods=['POST'])
def add_card_to_deck(deck_id):
    """Add a card to a deck"""
    try:
        data = request.json
        
        result = flashcard_service.add_card(
            deck_id=deck_id,
            front=data.get('front'),
            back=data.get('back'),
            hint=data.get('hint'),
            tags=data.get('tags')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/<card_id>', methods=['PUT'])
def update_card(card_id):
    """Update a flashcard"""
    try:
        data = request.json
        
        result = flashcard_service.update_card(
            card_id=card_id,
            front=data.get('front'),
            back=data.get('back'),
            hint=data.get('hint'),
            tags=data.get('tags')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a flashcard"""
    try:
        result = flashcard_service.delete_card(card_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/deck/<deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck"""
    try:
        result = flashcard_service.delete_deck(deck_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_flashcard_stats(user_id):
    """Get flashcard study statistics"""
    try:
        stats = flashcard_service.get_study_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcard_bp.route('/user/<user_id>/schedule', methods=['GET'])
def get_study_schedule(user_id):
    """Get study schedule (upcoming reviews)"""
    try:
        days = request.args.get('days', 7, type=int)
        
        schedule = flashcard_service.get_study_schedule(user_id, days)
        return jsonify({'schedule': schedule})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
