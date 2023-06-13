class Node:
    def __init__(self, char):
        """
        Represents a node in the Trie. Each node stores an array of links. The size is constant at 26 for the 26 lowercase alphabets and + 1 for the terminal(at index 0)
        :Input:
            char: The character representing the node
        :Time complexity: O(1)
        :Aux space complexity: O(1)        
        """
        self.links = [None] * 27  # O(1) time and space since it is fixed at 27
        self.char = char # the character at this node
        self.word = None # to store a reference to a sentence in the terminal node

        # the number of occurrences of a word. This is stored in every node so that we can compare the current inserted word's frequency with a node's current best word frequency
        # it is updated conditionally with each insertion involving this node. Refer to update_nodes() method
        self.word_freq = 0
        # reference to the child node that should be used during the traversal in autocomplete.
        # it is updated conditionally with each insertion involving this node. Refer to update_nodes() method 
        self.best_child = None

class CatsTrie:
    def __init__(self, sentences):
        """
        Represents a Trie data structure
        :Input:
            sentences: The list of strings available to be chosen when trying to autocompleting a prompt
        Note: M is the maximum length of a sentence in sentences and N is the number of sentences
        :Time complexity: O(NM) because each creates maximum M aux space and this is done N times  
        :Aux space complexity: O(NM) because each sentence uses maximum M aux space depending on length of sentence and this is done for N sentences
      
        """
        self.root = Node('R') # root node
        self.nodes_to_update = None # tracks the nodes that need to be updated for each string inserted
        # O(NM) where N = len(sentences) and M is the number of characters in the longest sentence
        for sentence in sentences: # N times
            self.insert_iterative(sentence) # O(M)

    def insert_iterative(self, sentence):
        """
        Iteratively inserts a node into the trie. It will only create a Node if the node does not previously exist. At the end of the insertion it calls update_nodes()
        to update all the node's best_child node and also the word_freq. 

        :Input: 
            sentence: string to be inserted
        :Postcondition: Each node points to the optimal child node for autocompleting
        :Time complexity: O(M)
        :Aux space complexity: O(M)   
        
        """
        self.nodes_to_update = []
        current_node = self.root

        # O(M)
        for char in sentence:
            index = ord(char) - 97 + 1 # returning the unicode value of a singlle character is O(1)

            # create node if it doesn't exist, O(1) 
            if current_node.links[index] is None:
                current_node.links[index] = Node(char)

            self.nodes_to_update.append(current_node) # update the nodes_to_update
            current_node = current_node.links[index] # move onto child node

        self.nodes_to_update.append(current_node) # update the nodes_to_update with the last character's node (e.g. for sentence 'abc' the last char is 'c') 

        # create terminal node if it does not exist, O(1)
        if current_node.links[0] is None:
            current_node.links[0] = Node('$')
        
        terminal_node = current_node.links[0]  # move onto terminal node
        terminal_node.word_freq += 1 # increment this word's frequency
        terminal_node.word = sentence # add a reference to the word in the terminal node, can be accessed during autocomplete
        self.nodes_to_update.append(terminal_node) # update the nodes_to_update with this terminal node

        # update all the nodes
        self.update_nodes()

    def update_nodes(self):
        """
        Initializes newly created nodes with their default child node, except for the terminal node
        Updates the node's best child node based on the frequency, followed by lexicographical ordering. 
        Example:
            Scenario: The word "abc" is inserted, so each character's best_child is initialized: R->a, a->b, b->c; their word_freq is the frequency of the word "abc" which is 1
                      The word "aba" is then inserted, since all the node's best_child frequencies are equal to the inserted word("aba")'s frequency, we look at lexicographical ordering.
                        * Root node: R's best child is 'a' which is same as new child 'a' so do nothing
                        * First char: 'a''s best child is 'b' which is same as new child 'b' so do nothing
                        * Second char: 'b''s best child is 'c' which is less than new child 'c' so change 'b''s best child to new child
                        * Third char: 'a''s best child is initialized and its word_freq = frequency of word "aba"(1)
                      The word "abc" is inserted again, now frequency of "abc" is 2 which is greater than all of the node's best_child frequency
                        * Root node: R's best child set to 'a'. No change to best_child, but R's word_freq is updated to 2
                        * First char: 'a''s best child set to 'b'. No change to best_child, but 'a''s word_freq is updated to 2
                        * Second char: 'c''s best child is set to '$'. No change to best_child, but 'c's word_freq is updated to 2
                      The word "aba" is inserted again, now all the node's best child frequencies are equal to the inserted word's frequency(2). Look at lexicographical ordering
                        * R, and a's best child and new child are the same so do nothing
                        * b's best child is 'c' and new child 'a' is less than 'c' so update b's best child to 'a'
        Note that since we are comparing a node with its child node in a for loop, updating the last node's word_freq has to be done separately outside the loop

        Note: M is the maximum length of a sentence in sentences and N is the number of sentences
        :Precondition: The word has been inserted into the Trie. 
        :Time complexity: O(2M) = O(M)
        :Aux space complexity: O(1)     
        
        """
        # O(M) where M is the length of the word
        # print(f"For {sentence} the first character changed is at index {self.firstCharChangedIndex}")
        for i in range(len(self.nodes_to_update)-1):
            node = self.nodes_to_update[i]
            if node.best_child is None:
                node.best_child = self.nodes_to_update[i+1]
                node.word_freq = self.nodes_to_update[-1].word_freq
            # print(f"{node.char}, current best child {node.best_child.char} current freq:{node.word_freq}, inserted word freq:{nodes_to_update[-1].word_freq} ")

        inserted_word_freq = self.nodes_to_update[-1].word_freq # O(1)
        # O(M) because the number of nodes to update is equal to the length of the word + 2 extra(1 for terminal 1 for root)
        for i in range(len(self.nodes_to_update)-1):
            node = self.nodes_to_update[i] # O(1)
            new_child = self.nodes_to_update[i+1] # O(1)

            # if new inserted word's frequency is greater than best child's word_freq, update the best child and word_freq of this node, O(1) operations
            if inserted_word_freq > node.best_child.word_freq:
                # print(f"New word {nodes_to_update[-1].word}({inserted_word_freq}) > {node.char}'s original best_child {node.best_child.char}'s freq of {node.best_child.word_freq}")
                node.best_child = new_child
                node.word_freq = inserted_word_freq

            # if frequency is the same and new child is lexicographically smaller than old best child, update the best child of this node, comparing single character is O(1)
            elif inserted_word_freq == node.best_child.word_freq and new_child.char < node.best_child.char:
                # print(f"New word {nodes_to_update[-1].word} and {node.best_child.char} same frequency, and new child {new_child.char} < {node.best_child.char}")
                node.best_child = new_child
            
        # update last node, O(1) operations
        if inserted_word_freq > self.nodes_to_update[-2].word_freq:
            # print(f"New word {nodes_to_update[-1].word}({inserted_word_freq}) > {nodes_to_update[-2].char}'s original best_child {nodes_to_update[-2].best_child.char}'s freq of {nodes_to_update[-2].best_child.word_freq}")
            self.nodes_to_update[-2].word_freq = inserted_word_freq

        # print("After update:")
        # for i in range(len(self.nodes_to_update)-1):
        #     node = self.nodes_to_update[i]
            # print(f"{node.char}, current best child {node.best_child.char} current freq:{node.word_freq}, inserted word freq:{nodes_to_update[-1].word_freq} ")

   
    def autoComplete(self, prompt):
        """
        Returns the most frequent autocompleted sentence based on the prompt. Tie breaker is using lexicographical ordering.
        This is done by traversing the Trie until the node of the last character of the prompt, and then continue traversing to reach the terminal where the word 
        can be retrieved via a reference.
        
        :Input:
            prompt: The prompt string to be autocompleted
        :Return:
            the most frequent autocompleted sentence, using lexicographical ordering as a tiebreaker if same frequency is encountered
        :Time complexity: O(X+Y), but if the prompt is invalid it will be just O(X)
        :Aux space complexity: O(1)           
        
        """
        node = self.root # start at root

        # iterate through prompt, O(X), where X is length of prompt. This always occurs
        for char in prompt:
            index = ord(char) - 97 + 1
            # if the character in the prompt does not exist, no options, so return None. This means the complexity of the function is O(X)
            if node.links[index] is None:
                return None
            node = node.links[index]

        # traverse Trie by iterating through the best_child of the nodes until the terminal is reached, where the word can be retrieved 
        # the part below is O(Y-X) where Y is the length of the autocompleted word
        current = node.best_child
        while current.char != '$':
            current = current.best_child
        return current.word