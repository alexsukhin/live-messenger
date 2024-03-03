class Tree {
    constructor() {
        this.root = null;
    }

    //Function to initialise the root value of the tree
    addRoot(value) {
        this.root = new TreeNode(value);
        return this.root;
    }

}

class TreeNode {
    constructor(value) {
        this.value = value;
        this.children = [];
    }

    //Function to add a child to a node
    addChild(value) {
        const newNode = new TreeNode(value);
        this.children.push(newNode);
        return newNode;
    }
}

class Queue {
    constructor() {
        this.elements = [];
    }

    //Enqueues an element onto the queue
    enqueue(element) {
        this.elements.push(element)
    }

    //Dequeues an element from the queue
    dequeue() {
        return this.elements.shift();
    }

    //Returns true if the queue is empty
    isEmpty() {
        return this.elements.length === 0;
    }
}

export function bfs(root) {

    //If there is no root to the tree, return an empty array
    if (!root) return [];

    const result = [];
    //Initialise the visited array as a set to ensure nodes with the same value are only represented as visited once
    const visited = new Set();
    const queue = new Queue();
    
    //Adds the first node's children to the queue and the visited array
    for (const child of root.children) {
        queue.enqueue(child)
        visited.add(child.value.userID);
    }

    while (!queue.isEmpty()) {
        //Dequeue the current node on the queue and push it to the final result array
        const currentNode = queue.dequeue();
        result.push(currentNode);

        //Adds the current node's children to the queue and the visited array if the child is not already in the visited array
        for (const child of currentNode.children) {
            child.parent = currentNode.value.username;
            if (!visited.has(child.value.userID)) {
                queue.enqueue(child)
                visited.add(child.value.userID)
            }
        }
    }

    //This filter function filters out the first node and the nodes children
    const filteredResult = result.filter(nodeValue => {

        if (nodeValue.value.userID === root.value) {
            return false;
        }

        for (const child of root.children) {
            if (nodeValue.value.userID === child.value.userID) {
                return false;
            }
        }

        return true;
    }) 

    return filteredResult;
}

export const tree = new Tree()

